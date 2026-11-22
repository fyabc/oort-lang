#! /usr/bin/env python

from typing import Generic, TypeVar

T = TypeVar("T")


class ASTVisitor(Generic[T]):
    def visit(self, node) -> T | None:
        return node.accept(self)

    def default_result(self) -> T | None:
        return None

    def aggregate_result(self, _aggregate: T | None, next_result: T | None) -> T | None:
        return next_result

    def pre_process(self, node):
        pass

    def post_process(self, node, result: T | None):
        return result

    def visit_children(self, node) -> T | None:
        result = self.default_result()
        if node is None:
            return result

        for child in node.children():
            if child is None:
                continue
            child_result = child.accept(self)
            result = self.aggregate_result(result, child_result)

        return result

    def visit_module(self, node) -> T | None:
        return self.visit_children(node)

    def visit_block_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_compiler_attribute(self, node) -> T | None:
        return self.visit_children(node)

    def visit_var_decl(self, node) -> T | None:
        return self.visit_children(node)

    def visit_import_stmt(self, node) -> T | None:
        return self.visit_children(node)

    def visit_import_from_stmt(self, node) -> T | None:
        return self.visit_children(node)

    def visit_assignment(self, node) -> T | None:
        return self.visit_children(node)

    def visit_attribute(self, node) -> T | None:
        return self.visit_children(node)

    def visit_subscript(self, node) -> T | None:
        return self.visit_children(node)

    def visit_call(self, node) -> T | None:
        return self.visit_children(node)

    def visit_macro_call(self, node) -> T | None:
        return self.visit_children(node)

    def visit_await_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_binary_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_unary_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_and_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_or_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_yield_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_return_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_continue_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_break_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_implicit_super_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_class_def(self, node) -> T | None:
        return self.visit_children(node)

    def visit_enum_def(self, node) -> T | None:
        return self.visit_children(node)

    def visit_interface_def(self, node) -> T | None:
        return self.visit_children(node)

    def visit_interface_method(self, node) -> T | None:
        return self.visit_children(node)

    def visit_enum_constructor(self, node) -> T | None:
        return self.visit_children(node)

    def visit_enum_field(self, node) -> T | None:
        return self.visit_children(node)

    def visit_match_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_match_arm(self, node) -> T | None:
        return self.visit_children(node)

    def visit_wildcard_pattern(self, node) -> T | None:
        return self.visit_children(node)

    def visit_name_pattern(self, node) -> T | None:
        return self.visit_children(node)

    def visit_constructor_pattern(self, node) -> T | None:
        return self.visit_children(node)

    def visit_literal_pattern(self, node) -> T | None:
        return self.visit_children(node)

    def visit_tuple_pattern(self, node) -> T | None:
        return self.visit_children(node)

    def visit_or_pattern(self, node) -> T | None:
        return self.visit_children(node)

    def visit_function_def(self, node) -> T | None:
        return self.visit_children(node)

    def visit_macro_def(self, node) -> T | None:
        return self.visit_children(node)

    def visit_if_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_for_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_while_expr(self, node) -> T | None:
        return self.visit_children(node)

    def visit_argument(self, node) -> T | None:
        return self.visit_children(node)

    def visit_parameter(self, node) -> T | None:
        return self.visit_children(node)

    def visit_type_parameter(self, node) -> T | None:
        return self.visit_children(node)

    def visit_single_decl_target(self, node) -> T | None:
        return self.visit_children(node)

    def visit_list_literal(self, node) -> T | None:
        return self.visit_children(node)

    def visit_tuple_literal(self, node) -> T | None:
        return self.visit_children(node)

    def visit_set_literal(self, node) -> T | None:
        return self.visit_children(node)

    def visit_dict_literal(self, node) -> T | None:
        return self.visit_children(node)

    def visit_slice_literal(self, node) -> T | None:
        return self.visit_children(node)

    def visit_int_constant(self, node) -> T | None:
        return self.visit_children(node)

    def visit_float_constant(self, node) -> T | None:
        return self.visit_children(node)

    def visit_string_constant(self, node) -> T | None:
        return self.visit_children(node)

    def visit_boolean_constant(self, node) -> T | None:
        return self.visit_children(node)

    def visit_null_constant(self, node) -> T | None:
        return self.visit_children(node)

    def visit_ellipsis_constant(self, node) -> T | None:
        return self.visit_children(node)

    def visit_name(self, node) -> T | None:
        return self.visit_children(node)
