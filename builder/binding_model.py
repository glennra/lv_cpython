"""Architecture-neutral metadata extracted from the LVGL header AST."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import ast as python_ast
import re

from pycparser import c_ast, c_generator


VA_LIST_REASON = (
    "va_list has a target-specific ABI and cannot be passed portably "
    "through CFFI"
)


@dataclass(frozen=True)
class TypeRef:
    spelling: str
    kind: str


@dataclass(frozen=True)
class Parameter:
    name: str | None
    type: TypeRef


@dataclass(frozen=True)
class Function:
    c_name: str
    python_name: str
    return_type: TypeRef
    parameters: tuple[Parameter, ...]
    variadic: bool = False
    method_owner: str | None = None
    method_name: str | None = None


@dataclass(frozen=True)
class Field:
    name: str | None
    type: TypeRef


@dataclass(frozen=True)
class Aggregate:
    c_name: str
    python_name: str
    kind: str
    fields: tuple[Field, ...]


@dataclass(frozen=True)
class Typedef:
    c_name: str
    python_name: str
    target: TypeRef
    callback: bool = False


@dataclass(frozen=True)
class EnumMember:
    c_name: str
    python_name: str
    value: str | None


@dataclass(frozen=True)
class Enum:
    c_name: str | None
    python_name: str | None
    members: tuple[EnumMember, ...]


@dataclass(frozen=True)
class Constant:
    c_name: str
    python_name: str
    type: TypeRef


@dataclass(frozen=True)
class Symbol:
    name: str
    value: str


@dataclass(frozen=True)
class Exclusion:
    c_name: str
    reason: str


@dataclass(frozen=True)
class BindingModel:
    generator_nodes: tuple[str, ...]
    functions: tuple[Function, ...]
    aggregates: tuple[Aggregate, ...]
    typedefs: tuple[Typedef, ...]
    enums: tuple[Enum, ...]
    constants: tuple[Constant, ...]
    symbols: tuple[Symbol, ...]
    exclusions: tuple[Exclusion, ...]


def python_name(c_name: str | None) -> str | None:
    if c_name is None:
        return None
    return c_name.removeprefix("lv_")


def _contains_identifier(node: c_ast.Node | None, name: str) -> bool:
    if node is None:
        return False
    if isinstance(node, c_ast.IdentifierType) and name in node.names:
        return True
    return any(
        _contains_identifier(child, name) for _, child in node.children()
    )


def _serialize_node(value) -> str:
    """Serialize pycparser nodes into py_builder's architecture-neutral IR."""
    if isinstance(value, list):
        return "[" + ", ".join(_serialize_node(item) for item in value) + "]"
    if not isinstance(value, c_ast.Node):
        return repr(value)

    attributes = (
        f"{name}={_serialize_node(getattr(value, name))}"
        for name in value.__slots__[:-2]
    )
    return f"{value.__class__.__name__}({', '.join(attributes)})"


def _is_fake_libc_node(node: c_ast.Node) -> bool:
    return bool(
        node.coord is not None
        and node.coord.file is not None
        and "fake_libc_include" in node.coord.file
    )


def unsupported_reason(node: c_ast.Node) -> str | None:
    if _contains_identifier(node, "va_list"):
        return VA_LIST_REASON
    return None


def filter_unsupported_declarations(
    ast: c_ast.FileAST,
) -> tuple[c_ast.FileAST, tuple[Exclusion, ...]]:
    """Remove unsupported top-level functions and report why."""
    retained = []
    exclusions = []
    for node in ast.ext:
        reason = None
        if isinstance(node, c_ast.Decl) and isinstance(
            node.type, c_ast.FuncDecl
        ):
            reason = unsupported_reason(node.type)

        if reason is None:
            retained.append(node)
        else:
            exclusions.append(Exclusion(node.name, reason))

    ast.ext = retained
    return ast, tuple(exclusions)


def _type_kind(node: c_ast.Node) -> str:
    if isinstance(node, c_ast.PtrDecl):
        return "pointer"
    if isinstance(node, c_ast.ArrayDecl):
        return "array"
    if isinstance(node, c_ast.FuncDecl):
        return "function"
    if isinstance(node, c_ast.Struct):
        return "struct"
    if isinstance(node, c_ast.Union):
        return "union"
    if isinstance(node, c_ast.Enum):
        return "enum"
    return "named"


def _type_spelling(node: c_ast.Node) -> str:
    if isinstance(node, c_ast.TypeDecl):
        qualifiers = " ".join(node.quals)
        spelling = _type_spelling(node.type)
        return f"{qualifiers} {spelling}".strip()
    if isinstance(node, c_ast.IdentifierType):
        return " ".join(node.names)
    if isinstance(node, c_ast.PtrDecl):
        qualifiers = " ".join(node.quals)
        pointer = "*" + (f" {qualifiers}" if qualifiers else "")
        return f"{_type_spelling(node.type)} {pointer}".strip()
    if isinstance(node, c_ast.ArrayDecl):
        dimension = (
            c_generator.CGenerator().visit(node.dim) if node.dim else ""
        )
        return f"{_type_spelling(node.type)}[{dimension}]"
    if isinstance(node, c_ast.FuncDecl):
        parameters, variadic = _parameters(node)
        rendered = [parameter.type.spelling for parameter in parameters]
        if variadic:
            rendered.append("...")
        return f"{_type_spelling(node.type)} ({', '.join(rendered)})"
    if isinstance(node, c_ast.Struct):
        return f"struct {node.name or '<anonymous>'}"
    if isinstance(node, c_ast.Union):
        return f"union {node.name or '<anonymous>'}"
    if isinstance(node, c_ast.Enum):
        return f"enum {node.name or '<anonymous>'}"
    return c_generator.CGenerator().visit(node)


def _type_ref(node: c_ast.Node) -> TypeRef:
    effective = node
    while isinstance(effective, c_ast.TypeDecl):
        effective = effective.type
    return TypeRef(_type_spelling(node), _type_kind(effective))


def _parameters(node: c_ast.FuncDecl) -> tuple[tuple[Parameter, ...], bool]:
    parameters = []
    variadic = False
    for parameter in node.args.params if node.args else ():
        if isinstance(parameter, c_ast.EllipsisParam):
            variadic = True
            continue
        parameters.append(Parameter(parameter.name, _type_ref(parameter.type)))
    return tuple(parameters), variadic


def _unwrap(node: c_ast.Node) -> c_ast.Node:
    while isinstance(node, (c_ast.TypeDecl, c_ast.PtrDecl, c_ast.ArrayDecl)):
        node = node.type
    return node


def _aggregate(node: c_ast.Node, declared_name: str | None) -> Aggregate | None:
    aggregate_node = _unwrap(node)
    if not isinstance(aggregate_node, (c_ast.Struct, c_ast.Union)):
        return None
    name = declared_name or aggregate_node.name
    if name is None:
        return None
    fields = tuple(
        Field(field.name, _type_ref(field.type))
        for field in aggregate_node.decls or ()
        if isinstance(field, c_ast.Decl)
    )
    return Aggregate(
        name,
        python_name(name),
        "struct" if isinstance(aggregate_node, c_ast.Struct) else "union",
        fields,
    )


def _enum(node: c_ast.Node, declared_name: str | None) -> Enum | None:
    enum_node = _unwrap(node)
    if not isinstance(enum_node, c_ast.Enum):
        return None
    members = tuple(
        EnumMember(
            enumerator.name,
            python_name(enumerator.name),
            c_generator.CGenerator().visit(enumerator.value)
            if enumerator.value is not None
            else None,
        )
        for enumerator in enum_node.values.enumerators
        if enum_node.values is not None
    )
    name = declared_name or enum_node.name
    return Enum(name, python_name(name), members)


def _function(node: c_ast.Decl) -> Function:
    parameters, variadic = _parameters(node.type)
    return Function(
        node.name,
        python_name(node.name),
        _type_ref(node.type.type),
        parameters,
        variadic,
    )


def _assign_method_owners(functions: list[Function]) -> list[Function]:
    constructors = {}
    for function in functions:
        if not function.python_name.endswith("_create"):
            continue
        owner = function.python_name.removesuffix("_create")
        constructors[owner] = function.return_type.spelling

    result = []
    owners = sorted(constructors, key=len, reverse=True)
    for function in functions:
        owner = next(
            (
                candidate
                for candidate in owners
                if function.python_name.startswith(candidate + "_")
            ),
            None,
        )
        if owner is None or not function.parameters:
            result.append(function)
            continue
        first_type = function.parameters[0].type.spelling.replace("const ", "")
        return_type = constructors[owner].replace("const ", "")
        if return_type.rstrip(" *") not in first_type:
            result.append(function)
            continue
        result.append(
            replace(
                function,
                method_owner=owner,
                method_name=function.python_name.removeprefix(owner + "_"),
            )
        )
    return result


_SYMBOL_PATTERN = re.compile(
    r'^\s*#define\s+LV_SYMBOL_([A-Z0-9_]+)\s+'
    r'("(?:\\.|[^"\\])*")'
)


def parse_symbols(path: str | Path) -> tuple[Symbol, ...]:
    symbols = []
    with Path(path).open(encoding="utf-8") as symbol_file:
        for line in symbol_file:
            match = _SYMBOL_PATTERN.match(line)
            if match is None:
                continue
            value = python_ast.literal_eval(match.group(2))
            symbols.append(
                Symbol(
                    match.group(1),
                    value.encode("latin1").decode("utf-8"),
                )
            )
    return tuple(symbols)


def build_binding_model(
    ast: c_ast.FileAST,
    *,
    symbol_header: str | Path | None = None,
) -> BindingModel:
    functions = []
    aggregates = []
    typedefs = []
    enums = []
    constants = []
    exclusions = []
    generator_nodes = []

    for node in ast.ext:
        if _is_fake_libc_node(node):
            continue

        function_decl = (
            node.decl if isinstance(node, c_ast.FuncDef) else node
        )
        if isinstance(function_decl, c_ast.Decl) and isinstance(
            function_decl.type, c_ast.FuncDecl
        ):
            reason = unsupported_reason(function_decl.type)
            if reason is not None:
                exclusions.append(Exclusion(function_decl.name, reason))
            else:
                functions.append(_function(function_decl))
                generator_nodes.append(_serialize_node(node))
            continue

        generator_nodes.append(_serialize_node(node))

        if isinstance(node, c_ast.Typedef):
            target = _type_ref(node.type)
            typedefs.append(
                Typedef(
                    node.name,
                    python_name(node.name),
                    target,
                    isinstance(_unwrap(node.type), c_ast.FuncDecl),
                )
            )
            aggregate = _aggregate(node.type, node.name)
            if aggregate is not None:
                aggregates.append(aggregate)
            enum = _enum(node.type, node.name)
            if enum is not None:
                enums.append(enum)
            continue

        if isinstance(node, c_ast.Decl):
            aggregate = _aggregate(node.type, node.name)
            if aggregate is not None:
                aggregates.append(aggregate)
            enum = _enum(node.type, node.name)
            if enum is not None:
                enums.append(enum)
            if node.name and node.name.isupper():
                constants.append(
                    Constant(node.name, python_name(node.name), _type_ref(node.type))
                )

    symbols = parse_symbols(symbol_header) if symbol_header else ()
    return BindingModel(
        tuple(generator_nodes),
        tuple(_assign_method_owners(functions)),
        tuple(aggregates),
        tuple(typedefs),
        tuple(enums),
        tuple(constants),
        tuple(symbols),
        tuple(exclusions),
    )
