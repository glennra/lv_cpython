"""Static model of the generated ``lvgl._raw`` Python API."""

from __future__ import annotations

from dataclasses import dataclass
import ast
import inspect
from pathlib import Path
import typing


@dataclass(frozen=True)
class RawFunction:
    name: str
    signature: inspect.Signature


@dataclass(frozen=True)
class RawClass:
    name: str
    bases: tuple[str, ...]


@dataclass(frozen=True)
class RawValue:
    name: str


@dataclass(frozen=True)
class RawApiModel:
    exports: tuple[tuple[str, RawFunction | RawClass | RawValue], ...]

    def items(self):
        return iter(self.exports)

    def class_is_subclass(self, value, base_name: str) -> bool:
        if not isinstance(value, RawClass):
            return False
        classes = {
            name: item
            for name, item in self.exports
            if isinstance(item, RawClass)
        }
        pending = [value]
        seen = set()
        while pending:
            candidate = pending.pop()
            if candidate.name in seen:
                continue
            seen.add(candidate.name)
            if candidate.name == base_name or base_name in candidate.bases:
                return True
            pending.extend(
                classes[name]
                for name in candidate.bases
                if name in classes
            )
        return False


class _AnnotationNamespace(dict):
    def __missing__(self, name):
        placeholder = type(name, (), {"__module__": "lvgl._raw"})
        self[name] = placeholder
        return placeholder


def _name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Subscript):
        return _name(node.value)
    return ast.unparse(node)


def _annotation(node: ast.expr | None, namespace) -> object:
    if node is None:
        return inspect.Signature.empty
    return eval(
        compile(ast.Expression(node), "<generated _raw annotation>", "eval"),
        namespace,
    )


def _signature(node: ast.FunctionDef, namespace) -> inspect.Signature:
    parameters = []
    positional = [*node.args.posonlyargs, *node.args.args]
    defaults = [None] * (len(positional) - len(node.args.defaults)) + [
        *node.args.defaults
    ]
    for index, (argument, default) in enumerate(zip(positional, defaults)):
        kind = (
            inspect.Parameter.POSITIONAL_ONLY
            if index < len(node.args.posonlyargs)
            else inspect.Parameter.POSITIONAL_OR_KEYWORD
        )
        parameters.append(
            inspect.Parameter(
                argument.arg,
                kind,
                default=(
                    inspect.Parameter.empty
                    if default is None
                    else RawValue(ast.unparse(default))
                ),
                annotation=_annotation(argument.annotation, namespace),
            )
        )
    if node.args.vararg is not None:
        parameters.append(
            inspect.Parameter(
                node.args.vararg.arg,
                inspect.Parameter.VAR_POSITIONAL,
                annotation=_annotation(node.args.vararg.annotation, namespace),
            )
        )
    for argument, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        parameters.append(
            inspect.Parameter(
                argument.arg,
                inspect.Parameter.KEYWORD_ONLY,
                default=(
                    inspect.Parameter.empty
                    if default is None
                    else RawValue(ast.unparse(default))
                ),
                annotation=_annotation(argument.annotation, namespace),
            )
        )
    if node.args.kwarg is not None:
        parameters.append(
            inspect.Parameter(
                node.args.kwarg.arg,
                inspect.Parameter.VAR_KEYWORD,
                annotation=_annotation(node.args.kwarg.annotation, namespace),
            )
        )
    return inspect.Signature(
        parameters,
        return_annotation=_annotation(node.returns, namespace),
    )


def parse_raw_api(path: str | Path) -> RawApiModel:
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    class_nodes = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }
    namespace = _AnnotationNamespace(
        {
            "typing": typing,
            "Union": typing.Union,
            "Any": typing.Any,
            "Callable": typing.Callable,
            "Optional": typing.Optional,
            "List": typing.List,
        }
    )
    for name in class_nodes:
        namespace[name]

    exports = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            exports.append((node.name, RawFunction(node.name, _signature(node, namespace))))
        elif isinstance(node, ast.ClassDef):
            exports.append(
                (
                    node.name,
                    RawClass(node.name, tuple(_name(base) for base in node.bases)),
                )
            )
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    exports.append((target.id, RawValue(target.id)))

    return RawApiModel(tuple(exports))
