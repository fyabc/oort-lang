#! /usr/bin/env python

"""Definite-assignment analysis for `oort-core` constructors.

The analysis is conservative and only covers the constructor body:

- slots with initializers start assigned;
- `this.slot = value` adds the slot on the current path;
- branches keep only slots assigned on every falling-through path;
- loop bodies never make later assignments definite;
- reads of `this.slot` before it is definitely assigned are reported;
- a `val` slot without an initializer may be assigned once, and never in a
  loop (the runtime rejects a second iteration assignment).
"""

import dataclasses
from collections.abc import Callable, Iterable

from ...ast import nodes
from ...source.source_position import SourcePosition


@dataclasses.dataclass(frozen=True, slots=True)
class SlotFact:
    """The bits of slot metadata the analysis needs."""

    name: str
    mutable: bool
    has_initializer: bool
    position: SourcePosition
    # Inherited slots can be initialized by `super.__init__(...)`.
    from_base: bool = False


@dataclasses.dataclass(slots=True)
class AssignState:
    definite: set[str]
    maybe: set[str]

    def copy(self) -> "AssignState":
        return AssignState(set(self.definite), set(self.maybe))


Reporter = Callable[[str, SourcePosition], None]


class DefiniteAssignmentAnalyzer:
    def __init__(self, slots: Iterable[SlotFact], report: Reporter):
        self.slots = {slot.name: slot for slot in slots}
        self.report = report
        self.loop_depth = 0

    def check(self, init: nodes.FunctionDef) -> None:
        initial = {slot.name for slot in self.slots.values() if slot.has_initializer}
        state = self._statements(init.body.statements, AssignState(set(initial), set(initial)))
        if state is not None:
            self._check_complete(state, init.position, "Constructor must initialize slot(s)")

    # ------------------------------------------------------------------
    # Statements and expressions
    # ------------------------------------------------------------------

    def _statements(
        self, statements: Iterable[nodes.ASTNode], state: AssignState | None
    ) -> AssignState | None:
        for stmt in statements:
            if state is None:
                return None
            state = self._stmt(stmt, state)
        return state

    def _block(self, block: nodes.BlockExpr, state: AssignState) -> AssignState | None:
        return self._statements(block.statements, state)

    def _stmt(self, node: nodes.ASTNode, state: AssignState) -> AssignState | None:
        if isinstance(node, nodes.VarDecl):
            if node.init_value is not None:
                return self._expr(node.init_value, state)
            return state
        return self._expr(node, state)

    def _expr(self, node: nodes.ASTNode | None, state: AssignState) -> AssignState | None:
        if node is None:
            return state
        if isinstance(node, (nodes.FunctionDef, nodes.ClassDef, nodes.EnumDef)):
            # Do not descend into nested scopes: they run later.
            return state
        if isinstance(node, nodes.Assignment):
            return self._assignment(node, state)
        if isinstance(node, nodes.Call) and self._is_super_init_call(node):
            next_state = self._children(node, state)
            if next_state is None:
                return None
            return self._mark_base_initialized(next_state, node.position)
        if isinstance(node, nodes.IfExpr):
            return self._if(node, state)
        if isinstance(node, nodes.MatchExpr):
            return self._match(node, state)
        if isinstance(node, nodes.BlockExpr):
            return self._block(node, state)
        if isinstance(node, nodes.WhileExpr):
            return self._while(node, state)
        if isinstance(node, nodes.ForExpr):
            return self._for(node, state)
        if isinstance(node, nodes.ReturnExpr):
            if node.value is not None:
                next_state = self._expr(node.value, state)
                if next_state is None:
                    return None
                state = next_state
            self._check_complete(
                state, node.position, "Constructor returns before initializing slot(s)"
            )
            return None
        if isinstance(node, nodes.BreakExpr):
            if node.value is not None:
                next_state = self._expr(node.value, state)
                if next_state is None:
                    return None
                state = next_state
            return None
        if isinstance(node, nodes.ContinueExpr):
            return None
        if isinstance(node, nodes.Attribute):
            slot_name = self._this_slot(node)
            if slot_name is not None:
                if slot_name in self.slots and slot_name not in state.definite:
                    self.report(
                        f"Slot '{slot_name}' is read before it is definitely assigned.",
                        node.position,
                    )
                return state
            return self._expr(node.value, state)

        return self._children(node, state)

    def _children(self, node: nodes.ASTNode, state: AssignState) -> AssignState | None:
        for _, child in node.named_children():
            if child is None:
                continue
            next_state = self._expr(child, state)
            if next_state is None:
                return None
            state = next_state
        return state

    @staticmethod
    def _is_super_init_call(node: nodes.Call) -> bool:
        func = node.func
        return (
            isinstance(func, nodes.Attribute)
            and isinstance(func.value, nodes.ImplicitSuperExpr)
            and func.attribute == "__init__"
        )

    def _mark_base_initialized(self, state: AssignState, position: SourcePosition) -> AssignState:
        """`super.__init__(...)` initializes inherited slots that lack initializers."""
        for slot in self.slots.values():
            if not slot.from_base or slot.has_initializer:
                continue
            if not slot.mutable and slot.name in state.maybe:
                self.report(
                    f"Read-only slot '{slot.name}' may already be assigned; "
                    "it can be assigned only once.",
                    position,
                )
                continue
            state.definite.add(slot.name)
            state.maybe.add(slot.name)
        return state

    def _assignment(self, node: nodes.Assignment, state: AssignState) -> AssignState | None:
        if node.op.text != "=":
            next_state = self._expr(node.rhs, state)
            if next_state is None:
                return None
            state = next_state
            if isinstance(node.lhs, nodes.Attribute):
                return self._expr(node.lhs.value, state)
            return self._expr(node.lhs, state)

        slot_name = self._this_slot(node.lhs)
        if slot_name is not None:
            next_state = self._expr(node.rhs, state)
            if next_state is None:
                return None
            state = next_state
            slot = self.slots.get(slot_name)
            if slot is None:
                return state
            if not slot.mutable:
                if slot.has_initializer:
                    self.report(
                        f"Cannot assign to read-only slot '{slot_name}'; it has an initializer.",
                        node.lhs.position,
                    )
                    return state
                if self.loop_depth > 0:
                    self.report(
                        f"Read-only slot '{slot_name}' cannot be assigned inside a loop.",
                        node.lhs.position,
                    )
                    return state
                if slot_name in state.maybe:
                    self.report(
                        f"Read-only slot '{slot_name}' may already be assigned; "
                        "it can be assigned only once.",
                        node.lhs.position,
                    )
                    return state
            state.definite.add(slot_name)
            state.maybe.add(slot_name)
            return state

        next_state = self._expr(node.rhs, state)
        if next_state is None:
            return None
        state = next_state
        if isinstance(node.lhs, nodes.Attribute):
            return self._expr(node.lhs.value, state)
        if isinstance(node.lhs, nodes.Subscript):
            next_state = self._expr(node.lhs.value, state)
            if next_state is None:
                return None
            state = next_state
            return self._expr(node.lhs.index, state)
        return self._expr(node.lhs, state)

    def _if(self, node: nodes.IfExpr, state: AssignState) -> AssignState | None:
        next_state = self._expr(node.condition, state)
        if next_state is None:
            return None
        state = next_state
        then_state = self._block(node.if_block, state.copy())
        if node.else_block is None:
            else_state: AssignState | None = state
        else:
            else_state = self._block(node.else_block, state.copy())
        return self._merge(then_state, else_state)

    def _match(self, node: nodes.MatchExpr, state: AssignState) -> AssignState | None:
        next_state = self._expr(node.scrutinee, state)
        if next_state is None:
            return None
        state = next_state
        result: AssignState | None = None
        for arm in node.arms:
            arm_state = self._expr(arm.body, state.copy())
            if arm_state is None:
                continue
            result = arm_state if result is None else self._merge(result, arm_state)
        return result if result is not None else None

    def _while(self, node: nodes.WhileExpr, state: AssignState) -> AssignState | None:
        next_state = self._expr(node.condition, state)
        if next_state is None:
            return None
        state = next_state
        self.loop_depth += 1
        try:
            body_state = self._block(node.body, state.copy())
        finally:
            self.loop_depth -= 1
        maybe = state.maybe | (body_state.maybe if body_state is not None else set())
        return AssignState(set(state.definite), maybe)

    def _for(self, node: nodes.ForExpr, state: AssignState) -> AssignState | None:
        next_state = self._expr(node.iterator, state)
        if next_state is None:
            return None
        state = next_state
        self.loop_depth += 1
        try:
            body_state = self._block(node.body, state.copy())
        finally:
            self.loop_depth -= 1
        maybe = state.maybe | (body_state.maybe if body_state is not None else set())
        return AssignState(set(state.definite), maybe)

    @staticmethod
    def _merge(left: AssignState | None, right: AssignState | None) -> AssignState | None:
        if left is None:
            return right
        if right is None:
            return left
        return AssignState(left.definite & right.definite, left.maybe | right.maybe)

    def _check_complete(self, state: AssignState, position: SourcePosition, prefix: str) -> None:
        missing = sorted(set(self.slots) - state.definite)
        if missing:
            self.report(f"{prefix}: {', '.join(missing)}.", position)

    @staticmethod
    def _this_slot(node: nodes.ASTNode) -> str | None:
        if (
            isinstance(node, nodes.Attribute)
            and isinstance(node.value, nodes.Name)
            and node.value.id == "this"
        ):
            return node.attribute
        return None
