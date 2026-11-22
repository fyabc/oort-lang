#! /usr/bin/env python


from .ast_visitor import ASTVisitor
from .nodes import ASTNode


def _name_line(node: ASTNode) -> str:
    str_attrs = node.str_attrs()
    str_attrs_v = ""
    if str_attrs:
        str_attrs_v = f"({str_attrs})"
    return f"{node.node_type}{str_attrs_v} {{"


class ASTPrinter(ASTVisitor[list[str]]):
    def __init__(
        self,
        indent: int = 2,
        recursive: bool = True,
        show_metadata: bool = False,
    ):
        self.indent = indent
        self.recursive = recursive
        self.show_metadata = show_metadata

    def parse(self, node: ASTNode) -> str:
        lines: list[str] = node.accept(self)
        return "\n".join(lines)

    def visit_children(self, node: ASTNode) -> list[str]:
        return self._visit_children(node, None, False)

    def _visit_children(
        self, node: ASTNode, custom_lines: list[str] | None, insert_after: bool
    ) -> list[str]:
        lines = [_name_line(node)]

        if self.show_metadata:
            metadata_l = []
            for key, value in node.metadata.items():
                # Skip None to simplify output.
                if value is None:
                    continue
                metadata_l.append(f"{key}={value!r}")
            metadata_s = ", ".join(metadata_l)
            lines.append(f"{self._indent_s}[Metadata] ({metadata_s})")

        if custom_lines and not insert_after:
            lines.extend(custom_lines)

        if not self.recursive:
            lines.append("}")
            return lines

        for name, child in node.named_children():
            if child is not None and child.synthetic:
                continue
            if child is None:
                child_lines = ["NULL"]
            else:
                child_lines = self.visit(child) or ["NULL"]
            child_lines[0] = f"({name}): {child_lines[0]}"
            lines.extend(self._indent_lines(child_lines))

        if custom_lines and insert_after:
            lines.extend(custom_lines)

        if len(lines) == 1:
            # For single line.
            lines[0] = lines[0] + "}"
        else:
            lines.append("}")

        return lines

    @property
    def _indent_s(self) -> str:
        return " " * self.indent

    def _indent_lines(self, lines: list[str]) -> list[str]:
        _indent_s = self._indent_s
        return [_indent_s + line for line in lines]

    # visit_module: pass

    # visit_block_expr: pass

    # visit_var_decl: pass

    # visit_import_stmt: pass

    # visit_assignment: pass

    # visit_attribute: pass

    # visit_subscript: pass

    # visit_call: pass

    # visit_macro_call: pass

    # visit_await_expr: pass

    # visit_binary_expr: pass

    # visit_unary_expr: pass

    # visit_and_expr: pass

    # visit_or_expr: pass

    # visit_yield_expr: pass

    # visit_return_expr: pass

    # visit_continue_expr: pass

    # visit_break_expr: pass

    # visit_class_def: pass

    # visit_function_def: pass

    # visit_macro_def: pass

    # visit_if_expr: pass

    # visit_for_expr: pass

    # visit_while_expr: pass

    # visit_argument: pass

    # visit_parameter: pass

    # visit_single_decl_target: pass

    # visit_list_literal: pass

    # visit_tuple_literal: pass

    # visit_set_literal: pass

    # visit_dict_literal: pass

    # visit_slice_literal: pass

    # visit_int_constant: pass

    # visit_float_constant: pass

    # visit_string_constant: pass

    # visit_boolean_constant: pass

    # visit_null_constant: pass

    # visit_ellipsis_constant: pass

    # visit_name: pass
