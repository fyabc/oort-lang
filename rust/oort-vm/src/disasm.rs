//! Text disassembly for `.obc` artifacts (kind=0/1/2).
//!
//! Mirrors `bytecode/disasm.py` and `bytecode/typed_disasm.py` closely enough
//! to inspect an artifact without the Python frontend. Descriptor constants
//! (classes, match tables, imports) are summarized rather than expanded.

use crate::obc::{Constant, Module, Proto};
use crate::opcodes::*;
use crate::typed::opcodes as typed_op;
use crate::typed::{TypedAdtDecl, TypedModule, TypedProto, TypedType};
use crate::vm::float_repr;

#[derive(Clone, Copy)]
struct Fields {
    op: u32,
    a: usize,
    b: usize,
    c: usize,
    bx: usize,
    sbx: i32,
}

fn fields(word: u32) -> Fields {
    Fields {
        op: word >> 24,
        a: ((word >> 16) & 0xFF) as usize,
        b: ((word >> 8) & 0xFF) as usize,
        c: (word & 0xFF) as usize,
        bx: (word & 0xFFFF) as usize,
        sbx: (word & 0xFFFF) as i32 - 0x8000,
    }
}

/// One-line preview of a constant-pool entry.
fn constant_preview(value: &Constant) -> String {
    match value {
        Constant::Null => "null".to_string(),
        Constant::Bool(flag) => flag.to_string(),
        Constant::Int(value) => value.to_string(),
        Constant::BigInt(value) => value.to_string(),
        Constant::Float(value) => float_repr(*value),
        Constant::Str(text) => format!("'{text}'"),
        Constant::Slots(slots) => format!("slots={slots:?}"),
        Constant::Class(spec) => format!("class {}", spec.name),
        Constant::Call(spec) => {
            format!(
                "call pos={} kws={}",
                spec.positional_count,
                spec.keywords.len()
            )
        }
        Constant::Enum(spec) => format!("enum {}", spec.name),
        Constant::Match(spec) => format!("match arms={}", spec.arms.len()),
        Constant::Import(spec) => format!("import '{}'", spec.module_path),
        Constant::Extension(spec) => format!("extension {}", spec.name),
    }
}

fn constant(proto: &Proto, index: usize) -> String {
    proto
        .constants
        .get(index)
        .map(constant_preview)
        .unwrap_or_else(|| format!("<bad K{index}>"))
}

fn typed_constant(proto: &TypedProto, index: usize) -> String {
    proto
        .constants
        .get(index)
        .map(constant_preview)
        .unwrap_or_else(|| format!("<bad k{index}>"))
}

fn format_dynamic(proto: &Proto, pc: usize, word: u32) -> String {
    let f = fields(word);
    let name = crate::opcodes::name(f.op).unwrap_or("?");
    match f.op {
        LOAD_K => format!("LOAD_K R{} K{}({})", f.a, f.bx, constant(proto, f.bx)),
        LOAD_L => format!("LOAD_L R{} L{}", f.a, f.b),
        STORE_L => format!("STORE_L L{} R{}", f.a, f.b),
        LOAD_G | STORE_G => format!("{name} R{} {}", f.a, constant(proto, f.bx)),
        DEF_FUN => format!("DEF_FUN proto[{}]", f.bx),
        MAKE_CLOSURE => format!("MAKE_CLOSURE R{} proto[{}]", f.a, f.bx),
        BUILD_CLASS => match proto.constants.get(f.bx) {
            Some(Constant::Class(spec)) => format!(
                "BUILD_CLASS R{} {} bases={} methods={}",
                f.a,
                spec.name,
                spec.base_count,
                spec.methods.len()
            ),
            _ => format!("BUILD_CLASS R{} <bad spec>", f.a),
        },
        BUILD_ENUM => match proto.constants.get(f.bx) {
            Some(Constant::Enum(spec)) => format!(
                "BUILD_ENUM R{} {} ctors={}",
                f.a,
                spec.name,
                spec.constructors.len()
            ),
            _ => format!("BUILD_ENUM R{} <bad spec>", f.a),
        },
        MATCH => match proto.constants.get(f.bx) {
            Some(Constant::Match(spec)) => format!("MATCH R{} arms={}", f.a, spec.arms.len()),
            _ => format!("MATCH R{} <bad spec>", f.a),
        },
        IMPORT => match proto.constants.get(f.bx) {
            Some(Constant::Import(spec)) => format!("IMPORT '{}'", spec.module_path),
            _ => "IMPORT <bad spec>".to_string(),
        },
        LOAD_OUTER => format!("LOAD_OUTER R{} depth={} slot={}", f.a, f.b, f.c),
        STORE_OUTER => format!("STORE_OUTER depth={} slot={} R{}", f.a, f.b, f.c),
        MOVE => format!("MOVE R{} R{}", f.a, f.b),
        ADD | SUB | MUL | DIV | FLOORDIV | MOD | POW | SHL | SHR | BAND | BOR | BXOR | EQ | NE
        | LT | LE | GT | GE | IN | NOT_IN | IS | IS_NOT => {
            format!("{name} R{} R{} R{}", f.a, f.b, f.c)
        }
        POS | NEG | INVERT | NOT => format!("{name} R{} R{}", f.a, f.b),
        JUMP => format!("JUMP {}", pc as i64 + 1 + f.sbx as i64),
        JUMP_FALSE | JUMP_TRUE => {
            format!("{name} R{} {}", f.a, pc as i64 + 1 + f.sbx as i64)
        }
        CALL => format!("CALL R{} nargs={}", f.a, f.c),
        RET => format!("RET R{}", f.a),
        OPEN_ITER => format!("OPEN_ITER R{} R{}", f.a, f.b),
        ITER_NEXT => format!("ITER_NEXT R{} R{} R{}", f.a, f.b, f.c),
        NEW_LIST | NEW_TUPLE | NEW_SET => {
            format!("{name} R{} base=R{} count={}", f.a, f.b, f.c)
        }
        NEW_DICT => format!("NEW_DICT R{} base=R{} pairs={}", f.a, f.b, f.c),
        GET_ITEM => format!("GET_ITEM R{} R{}[R{}]", f.a, f.b, f.c),
        SET_ITEM => format!("SET_ITEM R{}[R{}] = R{}", f.a, f.b, f.c),
        BUILD_SLICE => format!("BUILD_SLICE R{} base=R{} flags={:03b}", f.a, f.b, f.c),
        GET_ATTR | SET_ATTR => format!("{name} R{} {}", f.a, constant(proto, f.bx)),
        CALL_KW => match proto.constants.get(f.bx) {
            Some(Constant::Call(spec)) => format!(
                "CALL_KW R{} pos={} kws={}",
                f.a,
                spec.positional_count,
                spec.keywords.len()
            ),
            _ => format!("CALL_KW R{} <bad spec>", f.a),
        },
        UNPACK => format!(
            "UNPACK R{} -> R{}..R{}",
            f.a,
            f.b,
            f.b.saturating_add(f.c).saturating_sub(1)
        ),
        FRESH => format!("FRESH slots={}", constant(proto, f.bx)),
        SUPER => format!("SUPER R{} R{}", f.a, f.b),
        REGISTER_EXT => match proto.constants.get(f.bx) {
            Some(Constant::Extension(spec)) => {
                format!(
                    "REGISTER_EXT R{} {} proto[{}]",
                    f.a, spec.name, spec.function_index
                )
            }
            _ => format!("REGISTER_EXT R{} <bad spec>", f.a),
        },
        _ => format!("{name} A={} B={} C={}", f.a, f.b, f.c),
    }
}

fn format_dynamic_proto(proto: &Proto, prefix: &str) -> Vec<String> {
    let params = proto.params.join(", ");
    let mut lines = vec![format!(
        "{prefix}Proto {} regs={} params=({})",
        proto.name, proto.register_count, params
    )];
    for (pc, word) in proto.code.iter().enumerate() {
        let line = proto.positions.get(pc).map_or(0, |pos| pos.line);
        lines.push(format!(
            "{prefix}  {pc:4}  {}  ; line {line}",
            format_dynamic(proto, pc, *word)
        ));
    }
    lines
}

/// Disassemble a kind=0 module, main first and then each function.
pub(crate) fn disassemble_dynamic(module: &Module) -> String {
    let mut lines = format_dynamic_proto(&module.main, "");
    for (index, proto) in module.functions.iter().enumerate() {
        lines.push(String::new());
        lines.extend(format_dynamic_proto(proto, &format!("[{index}] ")));
    }
    lines.join("\n")
}

fn type_name(ty: &TypedType, decls: &[TypedAdtDecl]) -> String {
    match ty {
        TypedType::Int => "Int".to_string(),
        TypedType::Float => "Float".to_string(),
        TypedType::Bool => "Bool".to_string(),
        TypedType::Unit => "Unit".to_string(),
        TypedType::String => "String".to_string(),
        TypedType::Function => "Function".to_string(),
        TypedType::Iterator => "Iterator".to_string(),
        TypedType::List(item) => format!("List[{}]", type_name(item, decls)),
        TypedType::Set(item) => format!("Set[{}]", type_name(item, decls)),
        TypedType::Dict(key, value) => {
            format!(
                "Dict[{}, {}]",
                type_name(key, decls),
                type_name(value, decls)
            )
        }
        TypedType::Tuple(items) => {
            let parts: Vec<String> = items.iter().map(|item| type_name(item, decls)).collect();
            format!("Tuple[{}]", parts.join(", "))
        }
        TypedType::Adt(decl_id, args) => {
            let name = decls
                .get(*decl_id as usize)
                .map(|decl| decl.name.clone())
                .unwrap_or_else(|| format!("Adt{decl_id}"));
            if args.is_empty() {
                name
            } else {
                let parts: Vec<String> = args.iter().map(|arg| type_name(arg, decls)).collect();
                format!("{name}[{}]", parts.join(", "))
            }
        }
    }
}

fn format_typed(proto: &TypedProto, word: u32) -> String {
    let f = fields(word);
    let name = typed_op::name(f.op).unwrap_or("?");
    match f.op {
        typed_op::LOAD_K => format!("LOAD_K R{} k{}({})", f.a, f.bx, typed_constant(proto, f.bx)),
        typed_op::LOAD_L => format!("LOAD_L R{} slot{}", f.a, f.b),
        typed_op::STORE_L => format!("STORE_L slot{} R{}", f.a, f.b),
        typed_op::LOAD_G => format!("LOAD_G R{} {}", f.a, typed_constant(proto, f.bx)),
        typed_op::STORE_G => format!("STORE_G R{} {}", f.a, typed_constant(proto, f.bx)),
        typed_op::DEF_FUN => format!("DEF_FUN {} proto[{}]", typed_constant(proto, f.a), f.bx),
        typed_op::MOVE => format!("MOVE R{} R{}", f.a, f.b),
        typed_op::TO_FLOAT => format!("TO_FLOAT R{} R{}", f.a, f.b),
        typed_op::JMP => format!("JMP {}", f.bx),
        typed_op::JMP_FALSE | typed_op::JMP_TRUE => {
            format!("{name} R{} {}", f.a, f.bx)
        }
        typed_op::CALL => format!("CALL R{} argc={} -> R{}", f.a, f.b, f.c),
        typed_op::RET => format!("RET R{}", f.a),
        typed_op::POS_I | typed_op::POS_F | typed_op::NEG_I | typed_op::NEG_F | typed_op::NOT_B => {
            format!("{name} R{} R{}", f.a, f.b)
        }
        _ => format!("{name} R{} R{} R{}", f.a, f.b, f.c),
    }
}

fn format_typed_proto(proto: &TypedProto, decls: &[TypedAdtDecl]) -> Vec<String> {
    let params: Vec<String> = proto
        .param_types
        .iter()
        .map(|ty| type_name(ty, decls))
        .collect();
    let mut lines = vec![format!(
        "{}({}) -> {} registers={} words={}",
        proto.name,
        params.join(", "),
        type_name(&proto.ret_type, decls),
        proto.register_count,
        proto.code.len()
    )];
    if !proto.cells.is_empty() {
        let cells: Vec<String> = proto.cells.iter().map(|slot| slot.to_string()).collect();
        lines.push(format!("  cells: slot{}", cells.join(" slot")));
    }
    let types: Vec<String> = proto
        .register_types
        .iter()
        .enumerate()
        .map(|(index, type_id)| match type_id {
            Some(id) => proto
                .types
                .get(*id as usize)
                .map(|ty| format!("R{index}:{}", type_name(ty, decls)))
                .unwrap_or_else(|| format!("R{index}:?")),
            None => format!("R{index}:?"),
        })
        .collect();
    lines.push(format!("  register types: {}", types.join(" ")));
    for (pc, word) in proto.code.iter().enumerate() {
        lines.push(format!("  {pc:4}  {}", format_typed(proto, *word)));
    }
    lines
}

/// Disassemble a typed module (kind=1/2), main first and then each function.
pub(crate) fn disassemble_typed(module: &TypedModule) -> String {
    let decls = &module.adt_decls;
    let mut lines = format_typed_proto(&module.main, decls);
    for proto in &module.functions {
        lines.push(String::new());
        lines.extend(format_typed_proto(proto, decls));
    }
    lines.join("\n")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn constant_previews_are_stable() {
        assert_eq!(constant_preview(&Constant::Int(7)), "7");
        assert_eq!(constant_preview(&Constant::Float(2.0)), "2.0");
        assert_eq!(constant_preview(&Constant::Str("hi".into())), "'hi'");
        assert_eq!(constant_preview(&Constant::Null), "null");
    }

    #[test]
    fn typed_type_names_include_containers() {
        let ty = TypedType::List(Box::new(TypedType::Int));
        assert_eq!(type_name(&ty, &[]), "List[Int]");
        let pair = TypedType::Tuple(vec![TypedType::Int, TypedType::String]);
        assert_eq!(type_name(&pair, &[]), "Tuple[Int, String]");
    }

    #[test]
    fn opcode_names_cover_both_dialects() {
        assert_eq!(crate::opcodes::name(LOAD_K), Some("LOAD_K"));
        assert_eq!(
            crate::typed::opcodes::name(crate::typed::opcodes::ADD_I),
            Some("ADD_I")
        );
    }
}
