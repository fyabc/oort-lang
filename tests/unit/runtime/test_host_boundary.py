#! /usr/bin/env python

"""Host projection and native value-boundary tests."""

import pytest

from oort_lang.runtime import (
    OortDict,
    OortInstance,
    OortInt,
    OortList,
    OortTuple,
    Runtime,
)


def test_scalar_and_container_projection():
    runtime = Runtime()
    with runtime.activate():
        integer = OortInt(3)
        nested = OortList([OortInt(1), OortList([OortInt(2)])])

        assert runtime.host.to_host(integer) == 3
        assert runtime.host.to_host(nested) == [1, [2]]
        assert runtime.host.from_host(3).host_value == 3
        assert runtime.host.from_host([[1], 2]).host_value == [[1], 2]


def test_projection_preserves_aliases():
    runtime = Runtime()
    with runtime.activate():
        inner = OortList([OortInt(1)])
        outer = OortList([inner, inner])

        projected = outer.host_value

        assert projected == [[1], [1]]
        assert projected[0] is projected[1]


def test_self_referential_list_projection():
    runtime = Runtime()
    with runtime.activate():
        values = OortList([])
        values.value.append(values)

        projected = values.host_value

        assert projected[0] is projected


def test_self_referential_dict_projection():
    runtime = Runtime()
    with runtime.activate():
        mapping = OortDict({})
        mapping.value[OortInt(1)] = mapping

        projected = mapping.host_value

        assert projected[1] is projected


def test_cycle_through_tuple_is_rejected():
    runtime = Runtime()
    with runtime.activate():
        values = OortList([])
        wrapped = OortTuple((values,))
        values.value.append(wrapped)

        with pytest.raises(TypeError, match="cyclic tuple"):
            _ = wrapped.host_value


def test_user_instance_stays_an_oort_value():
    runtime = Runtime()
    with runtime.activate():
        instance = OortInstance(type_=runtime.types.object_type)
        assert instance.host_value is instance


def test_len_does_not_project_cyclic_containers(run_source):
    result = run_source(
        """\
var xs = [null]
xs[0] = xs
print(len(xs))
"""
    )
    assert result.stdout == "1\n"
