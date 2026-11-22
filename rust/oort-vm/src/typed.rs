//! Typed bytecode (`obc` kind=1) reader and unboxed VM (design 15 M4 U1).
//!
//! Scalar registers use `TypedValue` instead of boxed `vm::Value`: Int is i64,
//! Float is f64, Bool is bool, Unit carries no payload. Conversions happen only
//! at the native `print` boundary and when reporting the main result.
//! Semantics mirror the Python typed VM; see docs/design/16-numeric-semantics.md
//! for the Int/Float contract (i64 is a spike representation).

use std::cell::{Cell, RefCell};
use std::cmp::Ordering;
use std::collections::HashMap;
use std::rc::Rc;

use crate::obc::{Constant, Reader};
use crate::vm::{float_repr, floor_div, floor_mod, Value};

type TResult<T> = Result<T, String>;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TypedType {
    Int,
    Float,
    Bool,
    Unit,
    String,
    Function,
    List(Box<TypedType>),
    Set(Box<TypedType>),
    Dict(Box<TypedType>, Box<TypedType>),
    Tuple(Vec<TypedType>),
    Iterator,
}

#[derive(Debug, Clone)]
pub struct TypedProto {
    pub name: String,
    pub is_main: bool,
    pub register_count: u16,
    pub types: Vec<TypedType>,
    pub register_types: Vec<Option<u16>>,
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

fn read_type_table(r: &mut Reader<'_>, name: &str) -> TResult<Vec<TypedType>> {
    let count = r.u16()?;
    let mut types: Vec<TypedType> = Vec::with_capacity(count as usize);
    for _ in 0..count {
        let tag = r.u8()?;
        let ty = match tag {
            1 => TypedType::Int,
            2 => TypedType::Float,
            3 => TypedType::Bool,
            4 => TypedType::Unit,
            5 => TypedType::Function,
            6 => TypedType::String,
            7 | 8 => {
                let child = r.u16()? as usize;
                if child >= types.len() {
                    return Err(format!("typed proto '{name}' has a forward type reference"));
                }
                let inner = Box::new(types[child].clone());
                if tag == 7 {
                    TypedType::List(inner)
                } else {
                    TypedType::Set(inner)
                }
            }
            9 => {
                let key = r.u16()? as usize;
                let value = r.u16()? as usize;
                if key >= types.len() || value >= types.len() {
                    return Err(format!("typed proto '{name}' has a forward type reference"));
                }
                TypedType::Dict(Box::new(types[key].clone()), Box::new(types[value].clone()))
            }
            10 => {
                let mut elements = Vec::new();
                for _ in 0..r.u16()? {
                    let child = r.u16()? as usize;
                    if child >= types.len() {
                        return Err(format!("typed proto '{name}' has a forward type reference"));
                    }
                    elements.push(types[child].clone());
                }
                TypedType::Tuple(elements)
            }
            11 => TypedType::Iterator,
            _ => return Err(format!("invalid typed type tag {tag}")),
        };
        types.push(ty);
    }
    Ok(types)
}

fn type_at(types: &[TypedType], raw: u16, name: &str) -> TResult<TypedType> {
    if raw == 0 {
        return Err(format!(
            "typed proto '{name}' references an untyped parameter"
        ));
    }
    let index = (raw - 1) as usize;
    types
        .get(index)
        .cloned()
        .ok_or_else(|| format!("typed proto '{name}' has an out-of-range type id"))
}

fn read_proto(r: &mut Reader<'_>) -> TResult<TypedProto> {
    let name = r.string()?;
    let is_main = r.boolean()?;
    let types = read_type_table(r, &name)?;
    let register_count = r.u16()?;
    let mut register_types = Vec::with_capacity(register_count as usize);
    for _ in 0..register_count {
        let raw = r.u16()?;
        if raw == 0 {
            register_types.push(None);
        } else {
            let index = (raw - 1) as usize;
            if index >= types.len() {
                return Err(format!(
                    "typed proto '{name}' has an out-of-range register type"
                ));
            }
            register_types.push(Some(index as u16));
        }
    }
    let nparams = r.u8()?;
    let mut param_types = Vec::with_capacity(nparams as usize);
    for _ in 0..nparams {
        param_types.push(type_at(&types, r.u16()?, &name)?);
    }
    let ret_type = type_at(&types, r.u16()?, &name)?;
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
        types,
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
    if version != 4 {
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
    Unit,
    Bool(bool),
    Int(i64),
    Float(f64),
    Str(Rc<str>),
    List(Rc<RefCell<Vec<TypedValue>>>),
    Tuple(Rc<[TypedValue]>),
    Iterator(Rc<RefCell<TypedIterator>>),
    Function(usize),
    Native(TypedNative),
}

/// Snapshot iterator over a List, Tuple or String; mirrors `OortIterator`.
struct TypedIterator {
    values: Vec<TypedValue>,
    index: usize,
}

impl TypedIterator {
    fn next_value(&mut self) -> Option<TypedValue> {
        let value = self.values.get(self.index).cloned();
        if value.is_some() {
            self.index += 1;
        }
        value
    }
}

#[derive(Clone, Copy)]
enum TypedNative {
    Print,
    Len,
}

fn display_typed(value: &TypedValue) -> String {
    match value {
        TypedValue::Unit => "null".into(),
        TypedValue::Bool(b) => if *b { "true" } else { "false" }.into(),
        TypedValue::Int(i) => i.to_string(),
        TypedValue::Float(f) => float_repr(*f),
        TypedValue::Str(s) => s.to_string(),
        TypedValue::List(items) => {
            let parts: Vec<String> = items.borrow().iter().map(display_typed).collect();
            format!("[{}]", parts.join(", "))
        }
        TypedValue::Tuple(items) => {
            if items.len() == 1 {
                format!("({},)", display_typed(&items[0]))
            } else {
                let parts: Vec<String> = items.iter().map(display_typed).collect();
                format!("({})", parts.join(", "))
            }
        }
        TypedValue::Iterator(_) => "<iterator>".into(),
        TypedValue::Function(_) | TypedValue::Native(_) => "<function>".into(),
    }
}

fn to_value(value: TypedValue) -> TResult<Value> {
    typed_to_value(&value)
}

fn typed_to_value(value: &TypedValue) -> TResult<Value> {
    Ok(match value {
        TypedValue::Unit => Value::Null,
        TypedValue::Bool(b) => Value::Bool(*b),
        TypedValue::Int(i) => Value::Int(*i),
        TypedValue::Float(f) => Value::Float(*f),
        TypedValue::Str(s) => Value::Str(Rc::clone(s)),
        TypedValue::List(items) => {
            let mut values = Vec::with_capacity(items.borrow().len());
            for item in items.borrow().iter() {
                values.push(typed_to_value(item)?);
            }
            Value::List(Rc::new(RefCell::new(values)))
        }
        TypedValue::Tuple(items) => {
            let mut values = Vec::with_capacity(items.len());
            for item in items.iter() {
                values.push(typed_to_value(item)?);
            }
            Value::Tuple(Rc::from(values))
        }
        _ => return Err("typed main returned an iterable or function value".into()),
    })
}

fn typed_equal(lhs: &TypedValue, rhs: &TypedValue) -> TResult<bool> {
    Ok(match (lhs, rhs) {
        (TypedValue::Unit, TypedValue::Unit) => true,
        (TypedValue::Bool(a), TypedValue::Bool(b)) => a == b,
        (TypedValue::Int(a), TypedValue::Int(b)) => a == b,
        (TypedValue::Float(a), TypedValue::Float(b)) => a == b,
        (TypedValue::Int(a), TypedValue::Float(b)) => (*a as f64) == *b,
        (TypedValue::Float(a), TypedValue::Int(b)) => *a == (*b as f64),
        (TypedValue::Str(a), TypedValue::Str(b)) => a == b,
        (TypedValue::List(a), TypedValue::List(b)) => {
            let left = a.borrow();
            let right = b.borrow();
            left.len() == right.len()
                && left
                    .iter()
                    .zip(right.iter())
                    .all(|(l, r)| typed_equal(l, r).unwrap_or(false))
        }
        (TypedValue::Tuple(a), TypedValue::Tuple(b)) => {
            a.len() == b.len()
                && a.iter()
                    .zip(b.iter())
                    .all(|(l, r)| typed_equal(l, r).unwrap_or(false))
        }
        _ => false,
    })
}

fn constant_value(constant: &Constant) -> TResult<TypedValue> {
    Ok(match constant {
        Constant::Null => TypedValue::Unit,
        Constant::Bool(b) => TypedValue::Bool(*b),
        Constant::Int(i) => TypedValue::Int(*i),
        Constant::Float(f) => TypedValue::Float(*f),
        Constant::Str(s) => TypedValue::Str(Rc::clone(s)),
        _ => return Err("unsupported constant kind for typed LOAD_K".into()),
    })
}

fn as_int(value: &TypedValue) -> TResult<i64> {
    match value {
        TypedValue::Int(i) => Ok(*i),
        _ => Err("typed opcode expected Int".into()),
    }
}

fn as_float(value: &TypedValue) -> TResult<f64> {
    match value {
        TypedValue::Float(f) => Ok(*f),
        _ => Err("typed opcode expected Float".into()),
    }
}

fn as_bool(value: &TypedValue) -> TResult<bool> {
    match value {
        TypedValue::Bool(b) => Ok(*b),
        _ => Err("typed opcode expected Bool".into()),
    }
}

fn as_str(value: &TypedValue) -> TResult<&str> {
    match value {
        TypedValue::Str(s) => Ok(s.as_ref()),
        _ => Err("typed opcode expected String".into()),
    }
}

fn guard(expected: &TypedType, value: &TypedValue) -> TResult<()> {
    let ok = matches!(
        (expected, value),
        (TypedType::Int, TypedValue::Int(_))
            | (TypedType::Float, TypedValue::Float(_))
            | (TypedType::Bool, TypedValue::Bool(_))
            | (TypedType::String, TypedValue::Str(_))
            | (TypedType::Unit, TypedValue::Unit)
            | (TypedType::List(_), TypedValue::List(_))
            | (TypedType::Tuple(_), TypedValue::Tuple(_))
            | (TypedType::Iterator, TypedValue::Iterator(_))
    );
    if ok {
        Ok(())
    } else {
        Err(format!(
            "typed bytecode guard failed: expected {expected:?}"
        ))
    }
}

fn open_iterator(value: &TypedValue) -> TResult<TypedValue> {
    let values = match value {
        TypedValue::List(items) => items.borrow().clone(),
        TypedValue::Tuple(items) => items.to_vec(),
        TypedValue::Str(text) => text
            .chars()
            .map(|ch| TypedValue::Str(Rc::from(ch.to_string().as_str())))
            .collect(),
        _ => return Err("typed value is not iterable".into()),
    };
    Ok(TypedValue::Iterator(Rc::new(RefCell::new(TypedIterator {
        values,
        index: 0,
    }))))
}

fn iterator_next(value: &TypedValue) -> TResult<(TypedValue, bool)> {
    match value {
        TypedValue::Iterator(iterator) => {
            let mut iterator = iterator.borrow_mut();
            match iterator.next_value() {
                Some(value) => Ok((value, true)),
                None => Ok((TypedValue::Unit, false)),
            }
        }
        _ => Err("typed ITER_NEXT expects an iterator".into()),
    }
}

fn get_item(container: &TypedValue, index: &TypedValue) -> TResult<TypedValue> {
    let index = as_int(index)?;
    match container {
        TypedValue::List(items) => {
            let items = items.borrow();
            let position = normalize_index(index, items.len())?;
            Ok(items[position].clone())
        }
        TypedValue::Tuple(items) => {
            let position = normalize_index(index, items.len())?;
            Ok(items[position].clone())
        }
        TypedValue::Str(value) => {
            let chars: Vec<char> = value.chars().collect();
            let position = normalize_index(index, chars.len())?;
            Ok(TypedValue::Str(Rc::from(
                chars[position].to_string().as_str(),
            )))
        }
        _ => Err("typed indexing expects a List, Tuple or String".into()),
    }
}

fn normalize_index(index: i64, len: usize) -> TResult<usize> {
    let len_i64 = len as i64;
    let normalized = if index < 0 { index + len_i64 } else { index };
    if normalized < 0 || normalized >= len_i64 {
        return Err("index out of range".into());
    }
    Ok(normalized as usize)
}

fn mixed_cmp(lhs: &TypedValue, rhs: &TypedValue) -> TResult<Option<Ordering>> {
    match (lhs, rhs) {
        (TypedValue::Int(a), TypedValue::Int(b)) => Ok(Some(a.cmp(b))),
        (TypedValue::Float(a), TypedValue::Float(b)) => Ok(a.partial_cmp(b)),
        (TypedValue::Int(a), TypedValue::Float(b)) => Ok(cmp_i64_f64(*a, *b)),
        (TypedValue::Float(a), TypedValue::Int(b)) => {
            Ok(cmp_i64_f64(*b, *a).map(|ordering| ordering.reverse()))
        }
        _ => Err("typed mixed comparison expects Int or Float".into()),
    }
}

/// Exact comparison between i64 and f64 (no rounding of the integer).
fn cmp_i64_f64(i: i64, f: f64) -> Option<Ordering> {
    if f.is_nan() {
        return None;
    }
    if f == f64::INFINITY {
        return Some(Ordering::Less);
    }
    if f == f64::NEG_INFINITY {
        return Some(Ordering::Greater);
    }
    const TWO_POW_63: f64 = 9_223_372_036_854_775_808.0;
    if f >= TWO_POW_63 {
        return Some(Ordering::Less);
    }
    if f < -TWO_POW_63 {
        return Some(Ordering::Greater);
    }
    let truncated = f.trunc();
    let truncated_i128 = truncated as i128;
    match (i as i128).cmp(&truncated_i128) {
        Ordering::Equal => {
            let frac = f - truncated;
            if frac > 0.0 {
                Some(Ordering::Less)
            } else if frac < 0.0 {
                Some(Ordering::Greater)
            } else {
                Some(Ordering::Equal)
            }
        }
        ordering => Some(ordering),
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
const EQ_MIXED: u32 = 46;
const NE_MIXED: u32 = 47;
const LT_MIXED: u32 = 48;
const LE_MIXED: u32 = 49;
const GT_MIXED: u32 = 50;
const GE_MIXED: u32 = 51;
const ADD_S: u32 = 52;
const EQ_S: u32 = 53;
const NE_S: u32 = 54;
const LT_S: u32 = 55;
const LE_S: u32 = 56;
const GT_S: u32 = 57;
const GE_S: u32 = 58;
const NEW_LIST: u32 = 59;
const NEW_TUPLE: u32 = 60;
const GET_ITEM: u32 = 61;
const EQ_LIST: u32 = 62;
const NE_LIST: u32 = 63;
const EQ_TUPLE: u32 = 64;
const NE_TUPLE: u32 = 65;
const OPEN_ITER: u32 = 66;
const ITER_NEXT: u32 = 67;
const SET_ITEM: u32 = 68;

pub struct TypedVm {
    functions: Vec<ResolvedProto>,
    main: ResolvedProto,
    pool: FramePool,
    globals: GlobalTable,
}

/// Reusable register frames; LIFO reuse matches recursive call unwinding.
struct FramePool {
    frames: Vec<Vec<TypedValue>>,
}

impl FramePool {
    fn new() -> Self {
        FramePool {
            frames: Vec::with_capacity(16),
        }
    }

    fn acquire(&mut self, len: usize) -> Vec<TypedValue> {
        let mut frame = self.frames.pop().unwrap_or_default();
        frame.clear();
        frame.reserve(len.saturating_sub(frame.capacity()));
        frame.resize(len, TypedValue::Unit);
        frame
    }

    fn release(&mut self, frame: Vec<TypedValue>) {
        self.frames.push(frame);
    }
}

#[derive(Clone, Copy)]
enum TypedGlobal {
    Function(usize),
    Native(TypedNative),
}

/// A cached `LOAD_G` target. The version makes invalidation lazy: a globals
/// write bumps `GlobalTable::version`, and the next load refreshes the entry.
#[derive(Clone, Copy)]
struct CachedGlobal {
    version: u64,
    target: TypedGlobal,
}

/// Runtime global bindings. kind=1 currently has no writes (top-level
/// functions and `print` only), but the version hook lets a future `STORE_G`
/// invalidate caches without changing `.obc` or the resolver.
struct GlobalTable {
    version: u64,
    bindings: HashMap<String, TypedGlobal>,
}

impl GlobalTable {
    fn from_module(module: &TypedModule) -> Self {
        let mut bindings: HashMap<String, TypedGlobal> = module
            .functions
            .iter()
            .enumerate()
            .map(|(index, proto)| (proto.name.clone(), TypedGlobal::Function(index)))
            .collect();
        // A user function named `print` keeps precedence over the native.
        bindings
            .entry("print".to_string())
            .or_insert(TypedGlobal::Native(TypedNative::Print));
        bindings
            .entry("len".to_string())
            .or_insert(TypedGlobal::Native(TypedNative::Len));
        GlobalTable {
            version: 0,
            bindings,
        }
    }

    fn lookup(&self, name: &str) -> Option<TypedGlobal> {
        self.bindings.get(name).copied()
    }

    fn invalidate(&mut self) {
        self.version = self.version.wrapping_add(1);
    }
}

/// A proto plus its `LOAD_G` cache, keyed by constant-pool index.
struct ResolvedProto {
    proto: Rc<TypedProto>,
    globals: Vec<Cell<Option<CachedGlobal>>>,
}

fn resolve_globals(proto: &TypedProto, globals: &GlobalTable) -> Vec<Cell<Option<CachedGlobal>>> {
    proto
        .constants
        .iter()
        .map(|constant| match constant {
            Constant::Str(name) => match globals.lookup(name) {
                Some(target) => Cell::new(Some(CachedGlobal {
                    version: globals.version,
                    target,
                })),
                None => Cell::new(None),
            },
            _ => Cell::new(None),
        })
        .collect()
}

fn resolve_global(
    resolved: &ResolvedProto,
    globals: &GlobalTable,
    index: usize,
) -> TResult<TypedGlobal> {
    let entry = resolved
        .globals
        .get(index)
        .ok_or("invalid global constant index")?;
    if let Some(cached) = entry.get() {
        if cached.version == globals.version {
            return Ok(cached.target);
        }
    }
    let name = match resolved.proto.constants.get(index) {
        Some(Constant::Str(name)) => name.as_ref(),
        _ => return Err("invalid global name constant".into()),
    };
    let target = globals
        .lookup(name)
        .ok_or_else(|| format!("unknown name '{name}'"))?;
    entry.set(Some(CachedGlobal {
        version: globals.version,
        target,
    }));
    Ok(target)
}

impl TypedVm {
    pub fn new(module: TypedModule) -> Self {
        let globals = GlobalTable::from_module(&module);
        let functions = module
            .functions
            .iter()
            .map(|proto| ResolvedProto {
                proto: Rc::clone(proto),
                globals: resolve_globals(proto, &globals),
            })
            .collect();
        let main = ResolvedProto {
            proto: Rc::clone(&module.main),
            globals: resolve_globals(&module.main, &globals),
        };
        TypedVm {
            functions,
            main,
            pool: FramePool::new(),
            globals,
        }
    }

    /// Bump the globals version; cached `LOAD_G` targets refresh lazily.
    pub fn invalidate_globals(&mut self) {
        self.globals.invalidate();
    }

    pub fn run_main(&mut self) -> TResult<Value> {
        let functions = &self.functions;
        let main = &self.main;
        let globals = &self.globals;
        let pool = &mut self.pool;
        let mut frame = pool.acquire(main.proto.register_count as usize);
        let result = execute(main, functions, globals, pool, &mut frame);
        pool.release(frame);
        result.and_then(to_value)
    }
}

fn execute(
    resolved: &ResolvedProto,
    functions: &[ResolvedProto],
    globals: &GlobalTable,
    pool: &mut FramePool,
    registers: &mut [TypedValue],
) -> TResult<TypedValue> {
    let proto = &resolved.proto;
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
                registers[a] = constant_value(&proto.constants[bx])?;
            }
            LOAD_L | STORE_L => {
                registers[a] = registers[b].clone();
            }
            LOAD_G => {
                registers[a] = match resolve_global(resolved, globals, bx)? {
                    TypedGlobal::Function(index) => TypedValue::Function(index),
                    TypedGlobal::Native(native) => TypedValue::Native(native),
                };
            }
            DEF_FUN => {}
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
                        if right == -1 {
                            left.checked_neg().ok_or("integer overflow")?
                        } else {
                            floor_div(left, right)
                        }
                    }
                    _ => {
                        if right == 0 {
                            return Err("division or modulo by zero".into());
                        }
                        if right == -1 {
                            0
                        } else {
                            floor_mod(left, right)
                        }
                    }
                };
                registers[a] = TypedValue::Int(result);
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
                registers[a] = TypedValue::Float(result);
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
                registers[a] = TypedValue::Bool(result);
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
                registers[a] = TypedValue::Bool(result);
            }
            EQ_B | NE_B => {
                let left = as_bool(&registers[b])?;
                let right = as_bool(&registers[c])?;
                let result = if op == EQ_B {
                    left == right
                } else {
                    left != right
                };
                registers[a] = TypedValue::Bool(result);
            }
            EQ_MIXED | NE_MIXED | LT_MIXED | LE_MIXED | GT_MIXED | GE_MIXED => {
                let ordering = mixed_cmp(&registers[b], &registers[c])?;
                let result = match op {
                    EQ_MIXED => ordering == Some(Ordering::Equal),
                    NE_MIXED => ordering != Some(Ordering::Equal),
                    LT_MIXED => ordering == Some(Ordering::Less),
                    LE_MIXED => matches!(ordering, Some(Ordering::Less | Ordering::Equal)),
                    GT_MIXED => ordering == Some(Ordering::Greater),
                    _ => matches!(ordering, Some(Ordering::Greater | Ordering::Equal)),
                };
                registers[a] = TypedValue::Bool(result);
            }
            POS_I | NEG_I => {
                let value = as_int(&registers[b])?;
                registers[a] = TypedValue::Int(if op == NEG_I {
                    value.checked_neg().ok_or("integer overflow")?
                } else {
                    value
                });
            }
            POS_F | NEG_F => {
                let value = as_float(&registers[b])?;
                registers[a] = TypedValue::Float(if op == NEG_F { -value } else { value });
            }
            NOT_B => {
                let value = as_bool(&registers[b])?;
                registers[a] = TypedValue::Bool(!value);
            }
            TO_FLOAT => {
                let value = match &registers[b] {
                    TypedValue::Float(f) => *f,
                    TypedValue::Int(i) => *i as f64,
                    _ => return Err("TO_FLOAT expects a number".into()),
                };
                registers[a] = TypedValue::Float(value);
            }
            ADD_S => {
                let left = as_str(&registers[b])?;
                let right = as_str(&registers[c])?;
                registers[a] = TypedValue::Str(Rc::from(format!("{left}{right}").as_str()));
            }
            NEW_LIST => {
                let items = registers[a..a + b].to_vec();
                registers[c] = TypedValue::List(Rc::new(RefCell::new(items)));
            }
            NEW_TUPLE => {
                let items = registers[a..a + b].to_vec();
                registers[c] = TypedValue::Tuple(Rc::from(items));
            }
            GET_ITEM => {
                registers[a] = get_item(&registers[b], &registers[c])?;
            }
            OPEN_ITER => {
                registers[a] = open_iterator(&registers[b])?;
            }
            ITER_NEXT => {
                let (value, valid) = iterator_next(&registers[b])?;
                registers[a] = value;
                registers[c] = TypedValue::Bool(valid);
            }
            SET_ITEM => {
                let index = as_int(&registers[b])?;
                if let TypedValue::List(items) = &registers[a] {
                    let mut items = items.borrow_mut();
                    let position = normalize_index(index, items.len())?;
                    items[position] = registers[c].clone();
                } else {
                    return Err("typed SET_ITEM expects a List".into());
                }
            }
            EQ_LIST | NE_LIST | EQ_TUPLE | NE_TUPLE => {
                let mut equal = typed_equal(&registers[b], &registers[c])?;
                if op == NE_LIST || op == NE_TUPLE {
                    equal = !equal;
                }
                registers[a] = TypedValue::Bool(equal);
            }
            EQ_S | NE_S | LT_S | LE_S | GT_S | GE_S => {
                let left = as_str(&registers[b])?;
                let right = as_str(&registers[c])?;
                let result = match op {
                    EQ_S => left == right,
                    NE_S => left != right,
                    LT_S => left < right,
                    LE_S => left <= right,
                    GT_S => left > right,
                    _ => left >= right,
                };
                registers[a] = TypedValue::Bool(result);
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
                let result = call(
                    functions,
                    globals,
                    pool,
                    callee,
                    &registers[a + 1..a + 1 + b],
                )?;
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
    functions: &[ResolvedProto],
    globals: &GlobalTable,
    pool: &mut FramePool,
    callee: TypedValue,
    arguments: &[TypedValue],
) -> TResult<TypedValue> {
    match callee {
        TypedValue::Function(index) => {
            let resolved = functions.get(index).ok_or("invalid typed function index")?;
            let proto = &resolved.proto;
            if arguments.len() != proto.param_types.len() {
                return Err(format!(
                    "typed function '{}' expects {} arguments, got {}",
                    proto.name,
                    proto.param_types.len(),
                    arguments.len()
                ));
            }
            for (index, (expected, value)) in proto.param_types.iter().zip(arguments).enumerate() {
                guard(expected, value)
                    .map_err(|e| format!("argument {index} of '{}': {e}", proto.name))?;
            }
            let mut frame = pool.acquire(proto.register_count as usize);
            for (slot, value) in frame.iter_mut().zip(arguments) {
                *slot = value.clone();
            }
            let result = execute(resolved, functions, globals, pool, &mut frame);
            pool.release(frame);
            result
        }
        TypedValue::Native(TypedNative::Print) => {
            let parts: Vec<String> = arguments.iter().map(display_typed).collect();
            println!("{}", parts.join(" "));
            Ok(TypedValue::Unit)
        }
        TypedValue::Native(TypedNative::Len) => {
            if arguments.len() != 1 {
                return Err("len expects exactly one argument".into());
            }
            match &arguments[0] {
                TypedValue::Str(s) => Ok(TypedValue::Int(s.chars().count() as i64)),
                TypedValue::List(items) => Ok(TypedValue::Int(items.borrow().len() as i64)),
                TypedValue::Tuple(items) => Ok(TypedValue::Int(items.len() as i64)),
                _ => Err("len expects a String, List or Tuple in the typed subset".into()),
            }
        }
        _ => Err("typed bytecode call target is not callable".into()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn resolves_globals_once_per_proto() {
        let proto = TypedProto {
            name: "test".into(),
            is_main: false,
            register_count: 0,
            types: vec![],
            register_types: vec![],
            param_types: vec![],
            ret_type: TypedType::Unit,
            code: vec![],
            constants: vec![
                Constant::Str(Rc::from("f")),
                Constant::Str(Rc::from("print")),
                Constant::Str(Rc::from("missing")),
            ],
        };
        let globals = GlobalTable {
            version: 0,
            bindings: HashMap::from([
                ("f".to_string(), TypedGlobal::Function(0)),
                ("print".to_string(), TypedGlobal::Native(TypedNative::Print)),
            ]),
        };

        let cells = resolve_globals(&proto, &globals);
        assert!(matches!(
            cells[0].get().unwrap().target,
            TypedGlobal::Function(0)
        ));
        assert!(matches!(
            cells[1].get().unwrap().target,
            TypedGlobal::Native(TypedNative::Print)
        ));
        assert!(cells[2].get().is_none());
    }

    #[test]
    fn cached_globals_refresh_after_version_bump() {
        let proto = TypedProto {
            name: "g".into(),
            is_main: false,
            register_count: 0,
            types: vec![],
            register_types: vec![],
            param_types: vec![],
            ret_type: TypedType::Unit,
            code: vec![],
            constants: vec![Constant::Str(Rc::from("f"))],
        };
        let resolved = ResolvedProto {
            proto: Rc::new(proto),
            globals: vec![std::cell::Cell::new(None)],
        };
        let mut globals = GlobalTable {
            version: 0,
            bindings: HashMap::from([("f".to_string(), TypedGlobal::Function(0))]),
        };

        assert!(matches!(
            resolve_global(&resolved, &globals, 0).unwrap(),
            TypedGlobal::Function(0)
        ));

        globals.invalidate();
        globals
            .bindings
            .insert("f".to_string(), TypedGlobal::Native(TypedNative::Print));
        assert!(matches!(
            resolve_global(&resolved, &globals, 0).unwrap(),
            TypedGlobal::Native(TypedNative::Print)
        ));
        let cached = resolved.globals[0].get().unwrap();
        assert_eq!(cached.version, 1);
    }

    #[test]
    fn frame_pool_reuses_and_resets_frames() {
        let mut pool = FramePool::new();
        let mut first = pool.acquire(4);
        first[0] = TypedValue::Int(7);
        pool.release(first);

        let reused = pool.acquire(4);
        assert_eq!(reused.len(), 4);
        assert!(matches!(reused[0], TypedValue::Unit));

        let larger = pool.acquire(8);
        assert_eq!(larger.len(), 8);
    }

    #[test]
    fn mixed_comparison_is_exact_at_2_pow_53() {
        // 2^53 + 1 cannot be represented as f64; the comparison must not round.
        let big = TypedValue::Int(9_007_199_254_740_993);
        let as_float = TypedValue::Float(9_007_199_254_740_992.0);
        assert_eq!(mixed_cmp(&big, &as_float).unwrap(), Some(Ordering::Greater));
        assert_eq!(mixed_cmp(&as_float, &big).unwrap(), Some(Ordering::Less));
        assert_eq!(
            mixed_cmp(&TypedValue::Int(9_007_199_254_740_992), &as_float).unwrap(),
            Some(Ordering::Equal)
        );
    }

    #[test]
    fn mixed_comparison_handles_nan_and_infinity() {
        let nan = TypedValue::Float(f64::NAN);
        assert_eq!(mixed_cmp(&nan, &TypedValue::Int(1)).unwrap(), None);
        assert_eq!(mixed_cmp(&TypedValue::Int(1), &nan).unwrap(), None);
        assert_eq!(
            mixed_cmp(
                &TypedValue::Float(f64::INFINITY),
                &TypedValue::Int(i64::MAX)
            )
            .unwrap(),
            Some(Ordering::Greater)
        );
    }

    #[test]
    fn guard_rejects_wrong_types() {
        assert!(guard(&TypedType::Int, &TypedValue::Int(1)).is_ok());
        assert!(guard(&TypedType::Int, &TypedValue::Bool(true)).is_err());
        assert!(guard(&TypedType::Unit, &TypedValue::Unit).is_ok());
    }

    #[test]
    fn typed_values_display_like_python() {
        assert_eq!(display_typed(&TypedValue::Float(2.0)), "2.0");
        assert_eq!(display_typed(&TypedValue::Float(-0.0)), "-0.0");
        assert_eq!(display_typed(&TypedValue::Unit), "null");
    }
}
