#! /usr/bin/env python

"""Token post-processing: bracket tracking, newline filtering, completeness."""

import pytest
from antlr4 import InputStream, Token

from oort_lang.parser.grammar.OortLexer import OortLexer
from oort_lang.parser.token_processor import tokenize


def _process(text: str):
    return tokenize(OortLexer(InputStream(text)))


def _kinds(text: str) -> list[str]:
    return [
        OortLexer.symbolicNames[token.type]
        for token in _process(text).tokens
        if token.type != Token.EOF
    ]


@pytest.mark.parametrize(
    "text",
    [
        "(\n1\n)",
        "[\n1\n]",
        "@[\n]",
        "{:\n'a': 1\n:}",
        "{.\n1\n.}",
        "[([\n1\n])\n]",
    ],
)
def test_newlines_inside_brackets_are_dropped(text: str):
    assert "NEWLINE" not in _kinds(text)
    assert _process(text).bracket_depth == 0


def test_newlines_inside_code_blocks_are_kept():
    assert _kinds("{\n1\n}") == ["LBC", "NEWLINE", "DEC_INT", "NEWLINE", "RBC"]


def test_newlines_after_closing_bracket_are_kept():
    assert _kinds("(1)\n2") == ["LPA", "DEC_INT", "RPA", "NEWLINE", "DEC_INT"]


def test_code_block_inside_parentheses_keeps_its_newlines():
    assert _kinds("({ \n1\n}\n)") == [
        "LPA",
        "LBC",
        "NEWLINE",
        "DEC_INT",
        "NEWLINE",
        "RBC",
        "RPA",
    ]


def test_brackets_in_strings_and_comments_are_ignored():
    assert _process('"([{"').bracket_depth == 0
    assert _process("# ([{\n").bracket_depth == 0
    assert _process("'(\n'").bracket_depth == 0


@pytest.mark.parametrize("text", [")", "]", "}", ":}", ".}", ")]}"])
def test_unmatched_closing_brackets_do_not_crash(text: str):
    result = _process(text)
    assert result.bracket_depth == 0
    assert result.incomplete is False


def test_mismatched_closing_bracket_does_not_pop_the_wrong_opener():
    result = _process("([)]")
    assert result.bracket_depth == 1
    assert result.incomplete is True


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", False),
        ("1 + 2\n", False),
        ("(", True),
        ("(\n1\n", True),
        ("(\n1\n)", False),
        ("[1,\n", True),
        ("{:\n'a': 1\n:}", False),
        ("1 + \\\n", True),
        ("1 + \\\n2\n", False),
        ("1 + \\\n2\n3\n", False),
    ],
)
def test_incomplete_detection(text: str, expected: bool):
    assert _process(text).incomplete is expected


def test_line_escapes_are_removed_from_the_parser_stream():
    result = _process("1 + \\\n2\n")
    assert [token.text for token in result.tokens[:-1]] == ["1", "+", "2", "\n"]
    assert result.tokens[-1].type == Token.EOF
