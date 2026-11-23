#! /usr/bin/env python

"""Shared 32-bit bytecode: code objects, compiler, opcodes and disassembler."""

from .code import (
    BytecodeModule,
    CallSpec,
    ClassSpec,
    EnumSpec,
    ExtensionSpec,
    ImportSpec,
    MatchArmSpec,
    MatchSpec,
    PatternSpec,
    Proto,
)
from .compile import compile_module
from .disasm import disassemble_module, disassemble_proto
from .opcodes import (
    BINARY_OPCODES,
    UNARY_OPCODES,
    Decoded,
    Op,
    decode,
    encode_abc,
    encode_abx,
    encode_asbx,
    encode_ax,
)
from .typed_artifact import (
    TypedArtifact,
    TypedExport,
    TypedImport,
    build_typed_artifact,
    build_typed_artifacts,
    build_typed_program,
    build_typed_program_exports,
    link_typed_artifacts,
    read_linked_bundle,
    read_typed_artifact,
    write_linked_bundle,
    write_typed_artifact,
)
from .typed_compile import TypedProgram, TypedProto, compile_typed_module
from .typed_disasm import disassemble_typed_program
from .typed_opcodes import TypedOp
from .typed_serialize import read_typed_obc, write_typed_obc
from .typed_vm import TypedCodeFunction, TypedCodeVM

__all__ = [
    "BINARY_OPCODES",
    "UNARY_OPCODES",
    "BytecodeModule",
    "CallSpec",
    "ClassSpec",
    "Decoded",
    "EnumSpec",
    "ExtensionSpec",
    "ImportSpec",
    "MatchArmSpec",
    "MatchSpec",
    "Op",
    "PatternSpec",
    "Proto",
    "TypedArtifact",
    "TypedCodeFunction",
    "TypedCodeVM",
    "TypedExport",
    "TypedImport",
    "TypedOp",
    "TypedProgram",
    "TypedProto",
    "build_typed_artifact",
    "build_typed_artifacts",
    "build_typed_program",
    "build_typed_program_exports",
    "compile_module",
    "compile_typed_module",
    "decode",
    "disassemble_module",
    "disassemble_proto",
    "disassemble_typed_program",
    "encode_abc",
    "encode_abx",
    "encode_asbx",
    "encode_ax",
    "link_typed_artifacts",
    "read_linked_bundle",
    "read_typed_artifact",
    "read_typed_obc",
    "write_linked_bundle",
    "write_typed_artifact",
    "write_typed_obc",
]
