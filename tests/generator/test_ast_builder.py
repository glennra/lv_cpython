from pycparser import c_parser

from builder.ast_builder import _remove_va_list_functions


def test_remove_va_list_functions_keeps_variadic_functions():
    ast = c_parser.CParser().parse(
        """
        typedef char *va_list;
        int lv_vsnprintf(char *buffer, int count, const char *fmt, va_list va);
        int lv_snprintf(char *buffer, int count, const char *fmt, ...);
        int lv_tick_get(void);
        """
    )

    _remove_va_list_functions(ast)

    declarations = {
        node.name for node in ast.ext if getattr(node, "name", None)
    }
    assert "lv_vsnprintf" not in declarations
    assert "lv_snprintf" in declarations
    assert "lv_tick_get" in declarations
