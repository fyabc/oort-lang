#! /usr/bin/env python

from collections.abc import Iterable

from antlr4 import ParserRuleContext

from ..ast_visitor import ASTVisitor
from . import ASTNode
from .expressions import Expression


class Literal(Expression):
    def _accept(self, visitor: ASTVisitor):
        raise RuntimeError("Should not be called")


class ListLiteral(Literal):
    def __init__(self, context: ParserRuleContext, elements: Iterable[ASTNode]):
        super().__init__(context)
        self.elements = [element for element in elements]

    @property
    def node_type(self):
        return "List"

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, element in enumerate(self.elements):
            yield str(index), element

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_list_literal(self)


class TupleLiteral(Literal):
    def __init__(self, context: ParserRuleContext, elements: Iterable[ASTNode]):
        super().__init__(context)
        self.elements = [element for element in elements]

    @property
    def node_type(self):
        return "Tuple"

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, element in enumerate(self.elements):
            yield str(index), element

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_tuple_literal(self)


class SetLiteral(Literal):
    def __init__(self, context: ParserRuleContext, elements: Iterable[ASTNode]):
        super().__init__(context)
        self.elements = [element for element in elements]

    @property
    def node_type(self):
        return "Set"

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, element in enumerate(self.elements):
            yield str(index), element

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_set_literal(self)


class DictLiteral(Literal):
    def __init__(
        self,
        context: ParserRuleContext,
        items: Iterable[tuple[ASTNode | None, ASTNode]],
    ):
        super().__init__(context)
        self.items = [item for item in items]

    @property
    def node_type(self):
        return "Dict"

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, (key, value) in enumerate(self.items):
            yield f"key {index}", key
            yield f"value {index}", value

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_dict_literal(self)

    def key(self, idx: int):
        return self.items[idx][0]

    def value(self, idx: int):
        return self.items[idx][1]

    def keys(self):
        for key, _ in self.items:
            yield key

    def values(self):
        for _, value in self.items:
            yield value


class SliceLiteral(Literal):
    def __init__(
        self,
        context: ParserRuleContext,
        start: ASTNode | None,
        stop: ASTNode,
        step: ASTNode | None,
    ):
        super().__init__(context)
        self.start = start
        self.stop = stop
        self.step = step

    @property
    def node_type(self):
        return "Slice"

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "start", self.start
        yield "stop", self.stop
        yield "step", self.step

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_slice_literal(self)


class Constant(Literal):
    def str_attrs(self) -> str | None:
        return f"value={self.value}"


class IntConstant(Constant):
    def __init__(self, context: ParserRuleContext, value: int):
        super().__init__(context)
        self.value = value

    @property
    def node_type(self):
        return "Int"

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_int_constant(self)


class FloatConstant(Constant):
    def __init__(self, context: ParserRuleContext, value: float):
        super().__init__(context)
        self.value = value

    @property
    def node_type(self):
        return "Float"

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_float_constant(self)


class StringConstant(Constant):
    def __init__(self, context: ParserRuleContext, value: str):
        super().__init__(context)
        self.value = value

    @property
    def node_type(self):
        return "String"

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_string_constant(self)


class BooleanConstant(Constant):
    def __init__(self, context: ParserRuleContext, value: bool):
        super().__init__(context)
        self.value = value

    @property
    def node_type(self):
        return "Boolean"

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_boolean_constant(self)


class NullConstant(Constant):
    def __init__(self, context: ParserRuleContext):
        super().__init__(context)

    @property
    def value(self):
        return None

    @property
    def node_type(self):
        return "Null"

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_null_constant(self)


class EllipsisConstant(Constant):
    def __init__(self, context: ParserRuleContext):
        super().__init__(context)

    @property
    def value(self):
        return Ellipsis

    @property
    def node_type(self):
        return "Ellipsis"

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_ellipsis_constant(self)
