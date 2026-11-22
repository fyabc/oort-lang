//! Typed bytecode (`obc` kind=1) reader and VM (design 15, M4 entry).
//!
//! This slice executes the scalar typed subset: typed opcodes, TO_FLOAT,
//! CALL windows and entry guards. Values are still boxed `vm::Value` objects;
//! unboxed registers are a later M4 step. Semantics mirror
//! `oort_lang.bytecode.typed_vm`.

use std::collections::HashMap;
use std::rc::Rc;

use crate::obc::{Constant, Reader};
use crate::vm::{constant_to_value, display, floor_div, floor_mod, NativeFn, Value};

type TResult<T> = Result<T, String>;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TypedType {
    Int,
    Float,
    Bool,
    Unit,
    Function,
}

fn typed_type(tag: u8) -> TResult<Option<TypedType>> {
    Ok(match tag {
        0 => None,
        1 => Some(TypedType::Int),
        2 => Some(TypedType::Float),
        3 => Some(TypedType::Bool),
        4 => Some(TypedType::Unit),
        5 => Some(TypedType::Function),
        _ => return Err(format!("invalid typed register type tag {tag}")),
    })
}

#[derive(Debug, Clone)]
pub struct TypedProto {
    pub name: String,
    pub is_main: bool,
    pub register_count: u16,
    pub register_types: Vec<Option<TypedType>>,
    pub param_types: Vec<TypedType>,
    pub ret_type: TypedType,
    pub code: Vec<u32>,
    pub constants: Vec<Constant>,
}

#[derive(Debug, Clone)]
pub struct TypedModule {
    pub functions: Vec<Rc<TypedProto>>,
    pub main: Rc<TypedProto>,
}

fn read_proto(r: &mut Reader<'_>) -> TResult<TypedProto> {
    let name = r.string()?;
    let is_main = r.boolean()?;
    let register_count = r.u16()?;
    let mut register_types = Vec::with_capacity(register_count as usize);
    for _ in 0..register_count {
        register_types.push(typed_type(r.u8()?)?);
    }
    let nparams = r.u8()?;
    let mut param_types = Vec::with_capacity(nparams as usize);
    for _ in 0..nparams {
        let tag = r.u8()?;
        match typed_type(tag)? {
            Some(ty) => param_types.push(ty),
            None => return Err(format!("typed proto '{name}' has an untyped parameter")),
        }
    }
    let ret_type =
        typed_type(r.u8()?)?.ok_or_else(|| format!("typed proto '{name}' has no return type"))?;
    let ncode = r.u32()?;
    let mut code = Vec::with_capacity(ncode as usize);
    for _ in 0..ncode {
        code.push(r.u32()?);
    }
    let nconst = r.u32()?;
    let mut constants = Vec::with_capacity(nconst as usize);
    for _ in 0..nconst {
        constants.push(r.constant()?);
    }
    // Positions are diagnostic-only; skip them.
    if r.boolean()? {
        let _filename = r.string()?;
        let npos = r.u32()?;
        for _ in 0..npos {
            let _line = r.u32()?;
            let _column = r.i32()?;
        }
    }
    Ok(TypedProto {
        name,
        is_main,
        register_count,
        register_types,
        param_types,
        ret_type,
        code,
        constants,
    })
}

pub fn read_typed_module(data: &[u8]) -> TResult<TypedModule> {
    if data.len() < 5 || &data[0..3] != b"OBC" {
        return Err("not an Oort bytecode file (bad magic)".into());
    }
    let kind = data[3];
    if kind != 1 {
        return Err(format!("expected typed bytecode (kind=1), got kind={kind}"));
    }
    let version = data[4];
    if version != 1 {
        return Err(format!("unsupported typed bytecode version {version}"));
    }
    let mut r = Reader::new(&data[5..]);
    let nf = r.u32()?;
    let mut functions = Vec::with_capacity(nf as usize);
    for _ in 0..nf {
        functions.push(Rc::new(read_proto(&mut r)?));
    }
    let main = Rc::new(read_proto(&mut r)?);
    Ok(TypedModule { functions, main })
}

#[derive(Clone)]
enum TypedValue {
    Plain(Value),
    Function(usize),
    Native(NativeFn),
}

fn display_typed(value: &TypedValue) -> String {
    match value {
        TypedValue::Plain(v) => display(v),
        TypedValue::Function(_) | TypedValue::Native(_) => "<function>".into(),
    }
}

fn plain(value: &TypedValue) -> TResult<&Value> {
    match value {
        TypedValue::Plain(v) => Ok(v),
        _ => Err("typed opcode expected a plain value".into()),
    }
}

fn as_int(value: &TypedValue) -> TResult<i64> {
    match value {
        TypedValue::Plain(Value::Int(i)) => Ok(*i),
        _ => Err("typed opcode expected Int".into()),
    }
}

fn as_float(value: &TypedValue) -> TResult<f64> {
    match value {
        TypedValue::Plain(Value::Float(f)) => Ok(*f),
        _ => Err("typed opcode expected Float".into()),
    }
}

fn as_bool(value: &TypedValue) -> TResult<bool> {
    match value {
        TypedValue::Plain(Value::Bool(b)) => Ok(*b),
        _ => Err("typed opcode expected Bool".into()),
    }
}

fn guard(expected: TypedType, value: &TypedValue) -> TResult<()> {
    let ok = match (expected, value) {
        (TypedType::Int, TypedValue::Plain(Value::Int(_))) => true,
        (TypedType::Float, TypedValue::Plain(Value::Float(_))) => true,
        (TypedType::Bool, TypedValue::Plain(Value::Bool(_))) => true,
        (TypedType::Unit, TypedValue::Plain(Value::Null)) => true,
        _ => false,
    };
    if ok {
        Ok(())
    } else {
        Err(format!(
            "typed bytecode guard failed: expected {expected:?}"
        ))
    }
}

// Typed opcodes (bytecode/typed_opcodes.py).
const LOAD_K: u32 = 1;
const LOAD_L: u32 = 2;
const STORE_L: u32 = 3;
const LOAD_G: u32 = 4;
const DEF_FUN: u32 = 5;
const MOVE: u32 = 6;
const ADD_I: u32 = 10;
const ADD_F: u32 = 11;
const SUB_I: u32 = 12;
const SUB_F: u32 = 13;
const MUL_I: u32 = 14;
const MUL_F: u32 = 15;
const DIV_F: u32 = 16;
const FLOORDIV_I: u32 = 17;
const FLOORDIV_F: u32 = 18;
const MOD_I: u32 = 19;
const MOD_F: u32 = 20;
const EQ_I: u32 = 21;
const EQ_F: u32 = 22;
const EQ_B: u32 = 23;
const NE_I: u32 = 24;
const NE_F: u32 = 25;
const NE_B: u32 = 26;
const LT_I: u32 = 27;
const LT_F: u32 = 28;
const LE_I: u32 = 29;
const LE_F: u32 = 30;
const GT_I: u32 = 31;
const GT_F: u32 = 32;
const GE_I: u32 = 33;
const GE_F: u32 = 34;
const POS_I: u32 = 35;
const POS_F: u32 = 36;
const NEG_I: u32 = 37;
const NEG_F: u32 = 38;
const NOT_B: u32 = 39;
const TO_FLOAT: u32 = 40;
const JMP: u32 = 41;
const JMP_FALSE: u32 = 42;
const JMP_TRUE: u32 = 43;
const CALL: u32 = 44;
const RET: u32 = 45;

pub struct TypedVm {
    module: TypedModule,
    functions: HashMap<String, usize>,
}

impl TypedVm {
    pub fn new(module: TypedModule) -> Self {
        let functions = module
            .functions
            .iter()
            .enumerate()
            .map(|(index, proto)| (proto.name.clone(), index))
            .collect();
        TypedVm { module, functions }
    }

    pub fn run_main(&mut self) -> TResult<Value> {
        let main = Rc::clone(&self.module.main);
        let registers = vec![TypedValue::Plain(Value::Null); main.register_count as usize];
        let result = execute(&self.module, &self.functions, &main, registers)?;
        match result {
            TypedValue::Plain(value) => Ok(value),
            _ => Err("typed main returned a function value".into()),
        }
    }
}

fn execute(
    module: &TypedModule,
    functions: &HashMap<String, usize>,
    proto: &TypedProto,
    mut registers: Vec<TypedValue>,
) -> TResult<TypedValue> {
    let mut pc = 0usize;
    while pc < proto.code.len() {
        let word = proto.code[pc];
        let op = word >> 24;
        let a = ((word >> 16) & 0xFF) as usize;
        let b = ((word >> 8) & 0xFF) as usize;
        let c = (word & 0xFF) as usize;
        let bx = (word & 0xFFFF) as usize;

        match op {
            LOAD_K => {
                let constant = &proto.constants[bx];
                registers[a] = TypedValue::Plain(constant_to_value(constant)?);
            }
            LOAD_L | STORE_L => {
                registers[a] = registers[b].clone();
            }
            LOAD_G => {
                let name = match &proto.constants[bx] {
                    Constant::Str(s) => s.to_string(),
                    _ => return Err("invalid global name constant".into()),
                };
                registers[a] = match functions.get(&name) {
                    Some(index) => TypedValue::Function(*index),
                    None if name == "print" => TypedValue::Native(NativeFn::Print),
                    None => return Err(format!("unknown name '{name}'")),
                };
            }
            DEF_FUN => {
                // Functions are pre-bound by name; DEF_FUN is a no-op.
            }
            MOVE => {
                registers[a] = registers[b].clone();
            }
            ADD_I | SUB_I | MUL_I | FLOORDIV_I | MOD_I => {
                let left = as_int(&registers[b])?;
                let right = as_int(&registers[c])?;
                let result = match op {
                    ADD_I => left.checked_add(right).ok_or("integer overflow")?,
                    SUB_I => left.checked_sub(right).ok_or("integer overflow")?,
                    MUL_I => left.checked_mul(right).ok_or("integer overflow")?,
                    FLOORDIV_I => {
                        if right == 0 {
                            return Err("division or modulo by zero".into());
                        }
                        floor_div(left, right)
                    }
                    _ => {
                        if right == 0 {
                            return Err("division or modulo by zero".into());
                        }
                        floor_mod(left, right)
                    }
                };
                registers[a] = TypedValue::Plain(Value::Int(result));
            }
            ADD_F | SUB_F | MUL_F | DIV_F | FLOORDIV_F | MOD_F => {
                let left = as_float(&registers[b])?;
                let right = as_float(&registers[c])?;
                if matches!(op, DIV_F | FLOORDIV_F | MOD_F) && right == 0.0 {
                    return Err("division or modulo by zero".into());
                }
                let result = match op {
                    ADD_F => left + right,
                    SUB_F => left - right,
                    MUL_F => left * right,
                    DIV_F => left / right,
                    FLOORDIV_F => (left / right).floor(),
                    _ => left - (left / right).floor() * right,
                };
                registers[a] = TypedValue::Plain(Value::Float(result));
            }
            EQ_I | NE_I | LT_I | LE_I | GT_I | GE_I => {
                let left = as_int(&registers[b])?;
                let right = as_int(&registers[c])?;
                let result = match op {
                    EQ_I => left == right,
                    NE_I => left != right,
                    LT_I => left < right,
                    LE_I => left <= right,
                    GT_I => left > right,
                    _ => left >= right,
                };
                registers[a] = TypedValue::Plain(Value::Bool(result));
            }
            EQ_F | NE_F | LT_F | LE_F | GT_F | GE_F => {
                let left = as_float(&registers[b])?;
                let right = as_float(&registers[c])?;
                let result = match op {
                    EQ_F => left == right,
                    NE_F => left != right,
                    LT_F => left < right,
                    LE_F => left <= right,
                    GT_F => left > right,
                    _ => left >= right,
                };
                registers[a] = TypedValue::Plain(Value::Bool(result));
            }
            EQ_B | NE_B => {
                let left = as_bool(&registers[b])?;
                let right = as_bool(&registers[c])?;
                let result = if op == EQ_B {
                    left == right
                } else {
                    left != right
                };
                registers[a] = TypedValue::Plain(Value::Bool(result));
            }
            POS_I | NEG_I => {
                let value = as_int(&registers[b])?;
                registers[a] =
                    TypedValue::Plain(Value::Int(if op == NEG_I { -value } else { value }));
            }
            POS_F | NEG_F => {
                let value = as_float(&registers[b])?;
                registers[a] =
                    TypedValue::Plain(Value::Float(if op == NEG_F { -value } else { value }));
            }
            NOT_B => {
                let value = as_bool(&registers[b])?;
                registers[a] = TypedValue::Plain(Value::Bool(!value));
            }
            TO_FLOAT => {
                let value = match &registers[b] {
                    TypedValue::Plain(Value::Float(f)) => *f,
                    TypedValue::Plain(Value::Int(i)) => *i as f64,
                    _ => return Err("TO_FLOAT expects a number".into()),
                };
                registers[a] = TypedValue::Plain(Value::Float(value));
            }
            JMP => {
                pc = bx;
                continue;
            }
            JMP_FALSE => {
                if !as_bool(&registers[a])? {
                    pc = bx;
                    continue;
                }
            }
            JMP_TRUE => {
                if as_bool(&registers[a])? {
                    pc = bx;
                    continue;
                }
            }
            CALL => {
                let callee = registers[a].clone();
                let arguments: Vec<TypedValue> = registers[a + 1..a + 1 + b].to_vec();
                let result = call(module, functions, callee, arguments)?;
                registers[c] = result;
            }
            RET => {
                return Ok(registers[a].clone());
            }
            _ => return Err(format!("unknown typed opcode {op}")),
        }
        pc += 1;
    }
    Err(format!("typed function '{}' fell off the end", proto.name))
}

fn call(
    module: &TypedModule,
    _functions: &HashMap<String, usize>,
    callee: TypedValue,
    arguments: Vec<TypedValue>,
) -> TResult<TypedValue> {
    match callee {
        TypedValue::Function(index) => {
            let proto = &module.functions[index];
            if arguments.len() != proto.param_types.len() {
                return Err(format!(
                    "typed function '{}' expects {} arguments, got {}",
                    proto.name,
                    proto.param_types.len(),
                    arguments.len()
                ));
            }
            let mut registers = vec![TypedValue::Plain(Value::Null); proto.register_count as usize];
            for (index, (expected, value)) in proto.param_types.iter().zip(&arguments).enumerate() {
                guard(*expected, value)
                    .map_err(|e| format!("argument {index} of '{}': {e}", proto.name))?;
                registers[index] = value.clone();
            }
            execute(module, _functions, proto, registers)
        }
        TypedValue::Native(NativeFn::Print) => {
            let parts: Vec<String> = arguments.iter().map(display_typed).collect();
            println!("{}", parts.join(" "));
            Ok(TypedValue::Plain(Value::Null))
        }
        _ => Err("typed bytecode call target is not callable".into()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn typed_float_division_matches_python() {
        let left = TypedValue::Plain(Value::Float(7.0));
        let right = TypedValue::Plain(Value::Float(2.0));
        assert_eq!(as_float(&left).unwrap() / as_float(&right).unwrap(), 3.5);
    }

    #[test]
    fn typed_guard_rejects_wrong_types() {
        assert!(guard(TypedType::Int, &TypedValue::Plain(Value::Int(1))).is_ok());
        assert!(guard(TypedType::Int, &TypedValue::Plain(Value::Bool(true))).is_err());
        assert!(guard(TypedType::Unit, &TypedValue::Plain(Value::Null)).is_ok());
    }
}
