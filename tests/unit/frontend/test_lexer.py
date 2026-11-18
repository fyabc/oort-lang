#! /usr/bin/env python

"""Lexer tests."""

from antlr4 import InputStream

from oort_lang.parser.grammar.OortLexer import OortLexer


def _tokens(text: str) -> list[tuple[str, str]]:
    lexer = OortLexer(InputStream(text))
    result = []
    for token in lexer.getAllTokens():
        name = OortLexer.symbolicNames[token.type]
        result.append((name, token.text))
    return result


def test_integer_literals():
    assert _tokens("0 42 0b101 0o17 0x1F") == [
        ("DEC_INT", "0"),
        ("DEC_INT", "42"),
        ("BIN_INT", "0b101"),
        ("OCT_INT", "0o17"),
        ("HEX_INT", "0x1F"),
    ]


def test_float_literals():
    assert _tokens("1.5 2e3 1.5e-2") == [
        ("FLOAT_LITERAL", "1.5"),
        ("FLOAT_LITERAL", "2e3"),
        ("FLOAT_LITERAL", "1.5e-2"),
    ]


def test_string_literals():
    assert _tokens('"abc" r"\\n" \'x\'') == [
        ("STRING_LITERAL", '"abc"'),
        ("STRING_LITERAL", 'r"\\n"'),
        ("STRING_LITERAL", "'x'"),
    ]


def test_comments_are_skipped():
    assert _tokens("# comment\n42") == [("NEWLINE", "\n"), ("DEC_INT", "42")]


def test_newline_inside_brackets_is_ignored():
    tokens = _tokens("(\n1\n)\n2")
    assert tokens == [
        ("LPA", "("),
        ("DEC_INT", "1"),
        ("RPA", ")"),
        ("NEWLINE", "\n"),
        ("DEC_INT", "2"),
    ]


def test_newline_inside_braces_is_not_ignored():
    tokens = _tokens("{\n1\n}")
    assert tokens == [
        ("LBC", "{"),
        ("NEWLINE", "\n"),
        ("DEC_INT", "1"),
        ("NEWLINE", "\n"),
        ("RBC", "}"),
    ]


def test_user_operator_charset():
    # `.`, `:` and `@` are structural tokens, not user-operator characters.
    assert _tokens("+++") == [("USER_OP", "+++")]
    assert _tokens("a..b") == [
        ("IDENTIFIER", "a"),
        ("DOT", "."),
        ("DOT", "."),
        ("IDENTIFIER", "b"),
    ]
    assert _tokens("a::b") == [
        ("IDENTIFIER", "a"),
        ("DOUBLE_COLON", "::"),
        ("IDENTIFIER", "b"),
    ]
    assert _tokens("@@foo") == [("AT", "@"), ("AT", "@"), ("IDENTIFIER", "foo")]


def test_keywords_and_soft_keywords():
    tokens = _tokens("if else elif for while def class var val do in")
    assert tokens == [
        ("IF", "if"),
        ("ELSE", "else"),
        ("ELIF", "elif"),
        ("FOR", "for"),
        ("WHILE", "while"),
        ("DEF", "def"),
        ("CLASS", "class"),
        ("VAR", "var"),
        ("VAL", "val"),
        ("DO", "do"),
        ("IN", "in"),
    ]
