//! Spike register VM for type-erased Oort bytecode. Phase 0 subset: enough to
//! run the fib/loop/methods benchmarks and a handful of differential cases.
//! Semantics mirror `runtime/bytecode_vm.py` (frame layout, calling convention,
//! numeric rules). Integers keep an i64 fast path and promote to `BigInt` on
//! overflow, so big-int programs behave like Python. Unsupported opcodes fail
//! explicitly, never silently.

use std::cell::RefCell;
use std::cmp::Ordering;
use std::collections::HashMap;
use std::rc::Rc;
use std::time::Instant;

use num_bigint::BigInt;
use num_integer::Integer;
use num_rational::BigRational;
use num_traits::{ToPrimitive, Zero};

use crate::obc::{Constant, Module, Proto};

pub type Globals = HashMap<String, Value>;

/// A dynamic (kind=0) runtime value.
///
/// Register moves clone values; heap values therefore live behind `Rc` (and
/// `RefCell` where the language allows mutation). `Int` stays an inline i64
/// on the hot path; `Big` is the arbitrary-precision fallback. `Adt` is
/// (runtime name, payload), kept as it is in the Python VM.
#[derive(Clone)]
pub enum Value {
    Null,
    Bool(bool),
    Int(i64),
    /// An integer that overflowed `i64` (or arrived via a big constant).
    /// Arithmetic promotes to this on overflow and never narrows back,
    /// mirroring Python's arbitrary-precision ints.
    Big(Rc<BigInt>),
    Float(f64),
    Str(Rc<str>),
    List(Rc<RefCell<Vec<Value>>>),
    Tuple(Rc<[Value]>),
    Set(Rc<RefCell<Vec<Value>>>),
    Dict(Rc<RefCell<Vec<(Value, Value)>>>),
    Adt(Rc<str>, Vec<Value>),
    Closure(Rc<Closure>),
    BoundMethod(Rc<BoundMethod>),
    Type(Rc<TypeObj>),
    Instance(Rc<Instance>),
    Native(NativeFn),
    Iterator(Rc<RefCell<IterState>>),
}

#[derive(Clone, Copy)]
pub enum NativeFn {
    Print,
    Clock,
    Range,
}

pub struct Closure {
    pub proto_index: usize,
    pub defining_type: Option<Rc<TypeObj>>,
}

pub struct BoundMethod {
    pub this: Value,
    pub target: Value,
}

pub struct TypeObj {
    pub name: String,
    pub methods: RefCell<HashMap<String, Value>>,
}

pub struct Instance {
    pub ty: Rc<TypeObj>,
    pub fields: RefCell<HashMap<String, Value>>,
}

pub struct IterState {
    pub values: Vec<Value>,
    pub index: usize,
}

// Opcodes (spec 12 / opcodes.py).
const LOAD_K: u32 = 1;
const LOAD_L: u32 = 2;
const STORE_L: u32 = 3;
const LOAD_G: u32 = 4;
const STORE_G: u32 = 5;
const DEF_FUN: u32 = 6;
const MOVE: u32 = 7;
const ADD: u32 = 10;
const SUB: u32 = 11;
const MUL: u32 = 12;
const DIV: u32 = 13;
const FLOORDIV: u32 = 14;
const MOD: u32 = 15;
const EQ: u32 = 22;
const NE: u32 = 23;
const LT: u32 = 24;
const LE: u32 = 25;
const GT: u32 = 26;
const GE: u32 = 27;
const NEG: u32 = 36;
const POS: u32 = 35;
const INVERT: u32 = 37;
const NOT: u32 = 38;
const JUMP: u32 = 40;
const JUMP_FALSE: u32 = 41;
const JUMP_TRUE: u32 = 42;
const CALL: u32 = 43;
const RET: u32 = 44;
const OPEN_ITER: u32 = 45;
const ITER_NEXT: u32 = 46;
const GET_ATTR: u32 = 57;
const SET_ATTR: u32 = 58;
const BUILD_CLASS: u32 = 62;

type VResult<T> = Result<T, String>;

pub struct Vm {
    pub module: Module,
    pub globals: Globals,
    start: Instant,
}

impl Vm {
    pub fn new(module: Module) -> Self {
        let mut globals = Globals::new();
        globals.insert("print".into(), Value::Native(NativeFn::Print));
        globals.insert("clock".into(), Value::Native(NativeFn::Clock));
        globals.insert("range".into(), Value::Native(NativeFn::Range));
        Vm {
            module,
            globals,
            start: Instant::now(),
        }
    }

    pub fn run_main(&mut self) -> VResult<Value> {
        let main = Rc::clone(&self.module.main);
        execute(
            &self.module,
            &mut self.globals,
            &main,
            Vec::new(),
            None,
            self.start,
        )
    }
}

fn truthy(v: &Value) -> bool {
    match v {
        Value::Null => false,
        Value::Bool(b) => *b,
        Value::Int(i) => *i != 0,
        Value::Big(b) => !b.is_zero(),
        Value::Float(f) => *f != 0.0,
        Value::Str(s) => !s.is_empty(),
        Value::List(l) => !l.borrow().is_empty(),
        Value::Set(items) => !items.borrow().is_empty(),
        Value::Dict(entries) => !entries.borrow().is_empty(),
        Value::Adt(_, payload) => !payload.is_empty(),
        _ => true, // instances, types, callables are always truthy
    }
}

fn is_number(v: &Value) -> bool {
    matches!(v, Value::Int(_) | Value::Big(_) | Value::Float(_))
}

fn is_int(v: &Value) -> bool {
    matches!(v, Value::Int(_) | Value::Big(_))
}

fn as_bigint(v: &Value) -> Option<BigInt> {
    match v {
        Value::Int(i) => Some(BigInt::from(*i)),
        Value::Big(b) => Some((**b).clone()),
        _ => None,
    }
}

/// Exact comparison between an arbitrary-precision int and f64 (no rounding).
fn cmp_int_f64(i: &BigInt, f: f64) -> Option<Ordering> {
    if f.is_nan() {
        return None;
    }
    if f == f64::INFINITY {
        return Some(Ordering::Less);
    }
    if f == f64::NEG_INFINITY {
        return Some(Ordering::Greater);
    }
    let rational = BigRational::from_float(f)?;
    Some(BigRational::from_integer(i.clone()).cmp(&rational))
}

/// Exact numeric ordering; `None` for NaN, where every comparison is false.
fn numeric_cmp(lhs: &Value, rhs: &Value) -> Option<Ordering> {
    match (lhs, rhs) {
        (Value::Int(a), Value::Int(b)) => Some(a.cmp(b)),
        (Value::Big(a), Value::Big(b)) => Some(a.cmp(b)),
        (Value::Int(a), Value::Big(b)) => Some(BigInt::from(*a).cmp(b)),
        (Value::Big(a), Value::Int(b)) => Some(a.as_ref().cmp(&BigInt::from(*b))),
        (Value::Float(a), Value::Float(b)) => a.partial_cmp(b),
        (Value::Int(a), Value::Float(b)) => cmp_int_f64(&BigInt::from(*a), *b),
        (Value::Big(a), Value::Float(b)) => cmp_int_f64(a, *b),
        (Value::Float(a), Value::Int(b)) => {
            cmp_int_f64(&BigInt::from(*b), *a).map(Ordering::reverse)
        }
        (Value::Float(a), Value::Big(b)) => cmp_int_f64(b, *a).map(Ordering::reverse),
        _ => None,
    }
}

/// Mixed arithmetic converts ints to float; too-large ints are an explicit
/// error, matching Python's `OverflowError`.
fn numeric_to_f64(v: &Value) -> VResult<f64> {
    match v {
        Value::Int(i) => Ok(*i as f64),
        Value::Big(b) => b
            .to_f64()
            .filter(|f| f.is_finite())
            .ok_or_else(|| "integer too large to convert to float".to_string()),
        Value::Float(f) => Ok(*f),
        _ => Err(format!("Type '{}' is not numeric", type_name(v))),
    }
}

fn type_name(v: &Value) -> &'static str {
    match v {
        Value::Null => "Null",
        Value::Bool(_) => "Bool",
        Value::Int(_) | Value::Big(_) => "Int",
        Value::Float(_) => "Float",
        Value::Str(_) => "String",
        Value::List(_) => "List",
        Value::Tuple(_) => "Tuple",
        Value::Set(_) => "Set",
        Value::Dict(_) => "Dict",
        Value::Adt(_, _) => "ADT",
        Value::Closure(_) | Value::BoundMethod(_) | Value::Native(_) => "Function",
        Value::Type(_) => "Type",
        Value::Instance(_) => "Instance",
        Value::Iterator(_) => "Iterator",
    }
}

fn binary(op: u32, lhs: &Value, rhs: &Value) -> VResult<Value> {
    // Equality across types.
    if op == EQ || op == NE {
        let eq = match (lhs, rhs) {
            (Value::Null, Value::Null) => true,
            (Value::Bool(a), Value::Bool(b)) => a == b,
            (Value::Str(a), Value::Str(b)) => a == b,
            // Bool is not a number: `is_number` excludes it.
            _ if is_number(lhs) && is_number(rhs) => numeric_cmp(lhs, rhs) == Some(Ordering::Equal),
            _ => false,
        };
        return Ok(Value::Bool(if op == EQ { eq } else { !eq }));
    }

    // Ordering: numeric (Int/Float) or String.
    if matches!(op, LT | LE | GT | GE) {
        let ord = match (lhs, rhs) {
            (Value::Str(a), Value::Str(b)) => Some(a.cmp(b)),
            _ if is_number(lhs) && is_number(rhs) => numeric_cmp(lhs, rhs),
            _ => {
                return Err(format!(
                    "'{}' and '{}' are not orderable",
                    type_name(lhs),
                    type_name(rhs)
                ))
            }
        };
        // NaN has no ordering: every comparison is false, as in Python.
        let result = match ord {
            None => false,
            Some(ord) => match op {
                LT => ord == Ordering::Less,
                LE => ord != Ordering::Greater,
                GT => ord == Ordering::Greater,
                _ => ord != Ordering::Less,
            },
        };
        return Ok(Value::Bool(result));
    }

    // Integer arithmetic: stay on i64 while it fits, otherwise promote to
    // arbitrary precision. Both operands must be ints; mixed int/float goes
    // through the float path below.
    if is_int(lhs) && is_int(rhs) {
        if let (Value::Int(a), Value::Int(b)) = (lhs, rhs) {
            let (a, b) = (*a, *b);
            return Ok(match op {
                ADD => a
                    .checked_add(b)
                    .map(Value::Int)
                    .unwrap_or_else(|| Value::Big(Rc::new(BigInt::from(a) + BigInt::from(b)))),
                SUB => a
                    .checked_sub(b)
                    .map(Value::Int)
                    .unwrap_or_else(|| Value::Big(Rc::new(BigInt::from(a) - BigInt::from(b)))),
                MUL => a
                    .checked_mul(b)
                    .map(Value::Int)
                    .unwrap_or_else(|| Value::Big(Rc::new(BigInt::from(a) * BigInt::from(b)))),
                DIV => {
                    if b == 0 {
                        return Err("division by zero".into());
                    }
                    Value::Float(a as f64 / b as f64)
                }
                FLOORDIV => {
                    if b == 0 {
                        return Err("division or modulo by zero".into());
                    }
                    if a == i64::MIN && b == -1 {
                        Value::Big(Rc::new(-BigInt::from(a)))
                    } else {
                        Value::Int(floor_div(a, b))
                    }
                }
                MOD => {
                    if b == 0 {
                        return Err("modulo by zero".into());
                    }
                    if a == i64::MIN && b == -1 {
                        Value::Int(0)
                    } else {
                        Value::Int(floor_mod(a, b))
                    }
                }
                _ => return Err(format!("unsupported integer operator {op}")),
            });
        }
        let a = as_bigint(lhs).expect("checked integer");
        let b = as_bigint(rhs).expect("checked integer");
        return Ok(match op {
            ADD => Value::Big(Rc::new(a + b)),
            SUB => Value::Big(Rc::new(a - b)),
            MUL => Value::Big(Rc::new(a * b)),
            DIV => {
                if b.is_zero() {
                    return Err("division by zero".into());
                }
                Value::Float(numeric_to_f64(lhs)? / numeric_to_f64(rhs)?)
            }
            FLOORDIV => {
                if b.is_zero() {
                    return Err("division or modulo by zero".into());
                }
                Value::Big(Rc::new(a.div_floor(&b)))
            }
            MOD => {
                if b.is_zero() {
                    return Err("modulo by zero".into());
                }
                Value::Big(Rc::new(a.mod_floor(&b)))
            }
            _ => return Err(format!("unsupported integer operator {op}")),
        });
    }
    if is_number(lhs) && is_number(rhs) {
        let a = numeric_to_f64(lhs)?;
        let b = numeric_to_f64(rhs)?;
        return Ok(match op {
            ADD => Value::Float(a + b),
            SUB => Value::Float(a - b),
            MUL => Value::Float(a * b),
            DIV => {
                if b == 0.0 {
                    return Err("division by zero".into());
                }
                Value::Float(a / b)
            }
            FLOORDIV => {
                if b == 0.0 {
                    return Err("division or modulo by zero".into());
                }
                Value::Float((a / b).floor())
            }
            MOD => {
                if b == 0.0 {
                    return Err("modulo by zero".into());
                }
                Value::Float(a - b * (a / b).floor())
            }
            _ => return Err(format!("unsupported float operator {op}")),
        });
    }
    // String concatenation.
    if op == ADD {
        if let (Value::Str(a), Value::Str(b)) = (lhs, rhs) {
            return Ok(Value::Str(Rc::from(format!("{a}{b}").as_str())));
        }
    }
    Err(format!(
        "Type '{}' does not support operator",
        type_name(lhs)
    ))
}

pub(crate) fn floor_div(a: i64, b: i64) -> i64 {
    let q = a / b;
    let r = a % b;
    if r != 0 && (r < 0) != (b < 0) {
        q - 1
    } else {
        q
    }
}

pub(crate) fn floor_mod(a: i64, b: i64) -> i64 {
    let r = a % b;
    if r != 0 && (r < 0) != (b < 0) {
        r + b
    } else {
        r
    }
}

fn unary(op: u32, v: &Value) -> VResult<Value> {
    match op {
        NOT => Ok(Value::Bool(!truthy(v))),
        NEG => match v {
            Value::Int(i) => Ok(match i.checked_neg() {
                Some(neg) => Value::Int(neg),
                None => Value::Big(Rc::new(-BigInt::from(*i))),
            }),
            Value::Big(b) => Ok(Value::Big(Rc::new(-b.as_ref()))),
            Value::Float(f) => Ok(Value::Float(-f)),
            _ => Err(format!(
                "Type '{}' does not support unary '-'",
                type_name(v)
            )),
        },
        POS => match v {
            Value::Int(_) | Value::Big(_) | Value::Float(_) => Ok(v.clone()),
            _ => Err(format!(
                "Type '{}' does not support unary '+'",
                type_name(v)
            )),
        },
        INVERT => match v {
            Value::Int(i) => Ok(Value::Int(!i)),
            // Two's-complement invert on an unbounded integer: !x = -x - 1.
            Value::Big(b) => Ok(Value::Big(Rc::new(-b.as_ref() - 1))),
            _ => Err(format!("Type '{}' does not support '~'", type_name(v))),
        },
        _ => Err(format!("unsupported unary operator {op}")),
    }
}

pub fn float_repr(f: f64) -> String {
    if f.is_nan() {
        return "nan".into();
    }
    if f.is_infinite() {
        return if f > 0.0 { "inf".into() } else { "-inf".into() };
    }
    // Rust's Debug float formatting is the shortest round-trip form, but its
    // exponent spelling differs from Python's repr: Python always writes a
    // sign and at least two exponent digits (`1e+20`, `1e-05`).
    let s = format!("{f:?}");
    match s.split_once('e') {
        None => s,
        Some((mantissa, exponent)) => {
            let (sign, digits) = match exponent.strip_prefix('-') {
                Some(rest) => ('-', rest),
                None => ('+', exponent.strip_prefix('+').unwrap_or(exponent)),
            };
            let digits = if digits.len() < 2 {
                format!("0{digits}")
            } else {
                digits.to_string()
            };
            format!("{mantissa}e{sign}{digits}")
        }
    }
}

pub fn display(v: &Value) -> String {
    match v {
        Value::Null => "null".into(),
        Value::Bool(b) => if *b { "true" } else { "false" }.into(),
        Value::Int(i) => i.to_string(),
        Value::Big(b) => b.to_string(),
        Value::Float(f) => float_repr(*f),
        Value::Str(s) => s.to_string(),
        Value::List(l) => {
            let items: Vec<String> = l.borrow().iter().map(display).collect();
            format!("[{}]", items.join(", "))
        }
        Value::Tuple(items) => {
            if items.len() == 1 {
                format!("({},)", display(&items[0]))
            } else {
                let parts: Vec<String> = items.iter().map(display).collect();
                format!("({})", parts.join(", "))
            }
        }
        Value::Set(items) => {
            let items = items.borrow();
            if items.is_empty() {
                "{.}".into()
            } else {
                let parts: Vec<String> = items.iter().map(display).collect();
                format!("{{. {} .}}", parts.join(", "))
            }
        }
        Value::Dict(entries) => {
            let entries = entries.borrow();
            if entries.is_empty() {
                "{:}".into()
            } else {
                let parts: Vec<String> = entries
                    .iter()
                    .map(|(key, value)| format!("{}: {}", display(key), display(value)))
                    .collect();
                format!("{{: {} :}}", parts.join(", "))
            }
        }
        Value::Adt(name, payload) => {
            if payload.is_empty() {
                name.to_string()
            } else {
                let parts: Vec<String> = payload.iter().map(display).collect();
                format!("{}({})", name, parts.join(", "))
            }
        }
        Value::Type(t) => format!("<Type '{}'>", t.name),
        Value::Instance(inst) => format!("<{} object>", inst.ty.name),
        Value::Closure(_) | Value::BoundMethod(_) | Value::Native(_) => "<function>".into(),
        Value::Iterator(_) => "<iterator>".into(),
    }
}

pub(crate) fn constant_to_value(c: &Constant) -> VResult<Value> {
    Ok(match c {
        Constant::Null => Value::Null,
        Constant::Bool(b) => Value::Bool(*b),
        Constant::Int(i) => Value::Int(*i),
        Constant::BigInt(b) => Value::Big(Rc::clone(b)),
        Constant::Float(f) => Value::Float(*f),
        Constant::Str(s) => Value::Str(Rc::clone(s)),
        _ => return Err("unsupported constant kind for LOAD_K".into()),
    })
}

fn call_native(f: NativeFn, args: &[Value], start: Instant) -> VResult<Value> {
    match f {
        NativeFn::Print => {
            let parts: Vec<String> = args.iter().map(display).collect();
            println!("{}", parts.join(" "));
            Ok(Value::Null)
        }
        NativeFn::Clock => Ok(Value::Float(start.elapsed().as_secs_f64())),
        NativeFn::Range => {
            let (start_i, stop_i, step) = match args.len() {
                1 => (0, int_arg(&args[0])?, 1),
                2 => (int_arg(&args[0])?, int_arg(&args[1])?, 1),
                3 => (int_arg(&args[0])?, int_arg(&args[1])?, int_arg(&args[2])?),
                _ => return Err("range expects 1 to 3 arguments".into()),
            };
            if step == 0 {
                return Err("range step must not be zero".into());
            }
            let mut values = Vec::new();
            let mut i = start_i;
            while (step > 0 && i < stop_i) || (step < 0 && i > stop_i) {
                values.push(Value::Int(i));
                i += step;
            }
            Ok(Value::List(Rc::new(RefCell::new(values))))
        }
    }
}

fn int_arg(v: &Value) -> VResult<i64> {
    match v {
        Value::Int(i) => Ok(*i),
        Value::Big(b) => b
            .to_i64()
            .ok_or_else(|| "integer too large for range".to_string()),
        _ => Err("range arguments must be Int".into()),
    }
}

fn invoke(
    module: &Module,
    globals: &mut Globals,
    callee: &Value,
    args: Vec<Value>,
    start: Instant,
) -> VResult<Value> {
    match callee {
        Value::Closure(c) => {
            let proto = Rc::clone(&module.functions[c.proto_index]);
            execute(module, globals, &proto, args, None, start)
        }
        Value::BoundMethod(m) => {
            let target = m.target.clone();
            let this = m.this.clone();
            invoke_with_this(module, globals, &target, args, Some(this), start)
        }
        Value::Type(t) => {
            let instance = Value::Instance(Rc::new(Instance {
                ty: Rc::clone(t),
                fields: RefCell::new(HashMap::new()),
            }));
            if let Some(init) = t.methods.borrow().get("__init__").cloned() {
                invoke_with_this(module, globals, &init, args, Some(instance.clone()), start)?;
            } else if !args.is_empty() {
                return Err(format!(
                    "{}() takes 0 arguments but {} were given",
                    t.name,
                    args.len()
                ));
            }
            Ok(instance)
        }
        Value::Native(f) => call_native(*f, &args, start),
        _ => Err(format!("'{}' object is not callable", type_name(callee))),
    }
}

fn invoke_with_this(
    module: &Module,
    globals: &mut Globals,
    callee: &Value,
    args: Vec<Value>,
    this: Option<Value>,
    start: Instant,
) -> VResult<Value> {
    match callee {
        Value::Closure(c) => {
            let proto = Rc::clone(&module.functions[c.proto_index]);
            execute(module, globals, &proto, args, this, start)
        }
        Value::BoundMethod(m) => {
            let target = m.target.clone();
            let this = m.this.clone();
            invoke_with_this(module, globals, &target, args, Some(this), start)
        }
        _ => invoke(module, globals, callee, args, start),
    }
}

/// Run one proto on a fresh frame.
///
/// Frame layout matches the erased compiler: slot 0 holds `this` for methods,
/// positional parameters sit at their declared slots, and the remaining
/// registers are scratch. `CALL` expects the callee and arguments to be
/// contiguous (`R[A]` = callee, `R[A+1..A+1+C]` = arguments) and stores the
/// result at `R[A]`.
fn execute(
    module: &Module,
    globals: &mut Globals,
    proto: &Proto,
    args: Vec<Value>,
    this: Option<Value>,
    start: Instant,
) -> VResult<Value> {
    if proto.uses_cells {
        return Err(format!(
            "closure cells not supported in spike ({})",
            proto.name
        ));
    }
    let mut regs: Vec<Value> = vec![Value::Null; proto.register_count as usize];
    // Bind this (slot 0) and positional parameters by slot.
    let mut arg_iter = args.into_iter();
    if proto.has_this {
        if let Some(t) = this {
            regs[0] = t;
        }
    }
    for param in &proto.signature.params {
        if param.has_default || param.kind >= 2 {
            return Err(format!(
                "unsupported parameter kind in spike ({})",
                proto.name
            ));
        }
        if let Some(v) = arg_iter.next() {
            regs[param.slot as usize] = v;
        } else {
            return Err(format!("missing required argument '{}'", param.name));
        }
    }

    let code = &proto.code;
    let consts = &proto.constants;
    let mut pc: usize = 0;
    while pc < code.len() {
        // ABC fields are unsigned bytes; Bx is the low 16 bits and sBx is the
        // same bits biased by 0x8000 (signed jump offsets are relative).
        let word = code[pc];
        let op = word >> 24;
        let a = ((word >> 16) & 0xFF) as usize;
        let b = ((word >> 8) & 0xFF) as usize;
        let c = (word & 0xFF) as usize;
        let bx = (word & 0xFFFF) as usize;
        let sbx = (word & 0xFFFF) as i32 - 0x8000;

        match op {
            LOAD_K => regs[a] = constant_to_value(&consts[bx])?,
            LOAD_L => regs[a] = regs[b].clone(),
            STORE_L => regs[a] = regs[b].clone(),
            MOVE => regs[a] = regs[b].clone(),
            LOAD_G => {
                let name = const_str(&consts[bx])?;
                regs[a] = globals
                    .get(name)
                    .cloned()
                    .ok_or_else(|| format!("Name '{name}' is not defined"))?;
            }
            STORE_G => {
                let name = const_str(&consts[bx])?;
                globals.insert(name.to_string(), regs[a].clone());
            }
            DEF_FUN => {
                let fproto = &module.functions[bx];
                let closure = Value::Closure(Rc::new(Closure {
                    proto_index: bx,
                    defining_type: None,
                }));
                globals.insert(fproto.name.clone(), closure);
            }
            ADD | SUB | MUL | DIV | FLOORDIV | MOD | EQ | NE | LT | LE | GT | GE => {
                regs[a] = binary(op, &regs[b], &regs[c])?;
            }
            NEG | POS | INVERT | NOT => regs[a] = unary(op, &regs[b])?,
            JUMP => {
                pc = (pc as i64 + 1 + sbx as i64) as usize;
                continue;
            }
            JUMP_FALSE => {
                if !truthy(&regs[a]) {
                    pc = (pc as i64 + 1 + sbx as i64) as usize;
                    continue;
                }
            }
            JUMP_TRUE => {
                if truthy(&regs[a]) {
                    pc = (pc as i64 + 1 + sbx as i64) as usize;
                    continue;
                }
            }
            CALL => {
                let callee = regs[a].clone();
                let call_args: Vec<Value> = regs[a + 1..a + 1 + c].to_vec();
                regs[a] = invoke(module, globals, &callee, call_args, start)?;
            }
            RET => return Ok(regs[a].clone()),
            OPEN_ITER => {
                let values = match &regs[b] {
                    Value::List(l) => l.borrow().clone(),
                    Value::Str(s) => s
                        .chars()
                        .map(|ch| Value::Str(Rc::from(ch.to_string().as_str())))
                        .collect(),
                    _ => return Err(format!("'{}' is not iterable", type_name(&regs[b]))),
                };
                regs[a] = Value::Iterator(Rc::new(RefCell::new(IterState { values, index: 0 })));
            }
            ITER_NEXT => {
                let iter = match &regs[b] {
                    Value::Iterator(it) => Rc::clone(it),
                    _ => return Err("iterator expected".into()),
                };
                let mut state = iter.borrow_mut();
                if state.index < state.values.len() {
                    regs[a] = state.values[state.index].clone();
                    state.index += 1;
                    regs[c] = Value::Bool(true);
                } else {
                    regs[a] = Value::Null;
                    regs[c] = Value::Bool(false);
                }
            }
            BUILD_CLASS => {
                let spec = match &consts[bx] {
                    Constant::Class(s) => s,
                    _ => return Err("Invalid class descriptor".into()),
                };
                if spec.base_count != 0 || spec.has_metaclass {
                    return Err("inheritance/metaclass not supported in spike".into());
                }
                let ty = Rc::new(TypeObj {
                    name: spec.name.clone(),
                    methods: RefCell::new(HashMap::new()),
                });
                for (name, index) in &spec.methods {
                    let closure = Value::Closure(Rc::new(Closure {
                        proto_index: *index as usize,
                        defining_type: Some(Rc::clone(&ty)),
                    }));
                    ty.methods.borrow_mut().insert(name.clone(), closure);
                }
                regs[a] = Value::Type(ty);
            }
            GET_ATTR => {
                let name = const_str(&consts[bx])?;
                let receiver = regs[a].clone();
                regs[a] = get_attr(&receiver, name)?;
            }
            SET_ATTR => {
                let name = const_str(&consts[bx])?;
                let value = regs[a + 1].clone();
                match &regs[a] {
                    Value::Instance(inst) => {
                        inst.fields.borrow_mut().insert(name.to_string(), value);
                    }
                    _ => return Err(format!("Cannot set attribute on '{}'", type_name(&regs[a]))),
                }
            }
            _ => return Err(format!("Bytecode VM does not support opcode {op}")),
        }
        pc += 1;
    }
    Ok(Value::Null)
}

fn const_str(c: &Constant) -> VResult<&str> {
    match c {
        Constant::Str(s) => Ok(s),
        _ => Err("expected string constant".into()),
    }
}

fn get_attr(receiver: &Value, name: &str) -> VResult<Value> {
    match receiver {
        Value::Instance(inst) => {
            if let Some(v) = inst.fields.borrow().get(name) {
                return Ok(v.clone());
            }
            if let Some(m) = inst.ty.methods.borrow().get(name) {
                return Ok(Value::BoundMethod(Rc::new(BoundMethod {
                    this: receiver.clone(),
                    target: m.clone(),
                })));
            }
            Err(format!(
                "'{}' object has no attribute '{name}'",
                inst.ty.name
            ))
        }
        Value::Type(t) => t
            .methods
            .borrow()
            .get(name)
            .cloned()
            .ok_or_else(|| format!("Type '{}' has no attribute '{name}'", t.name)),
        _ => Err(format!(
            "'{}' object has no attribute '{name}'",
            type_name(receiver)
        )),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn floor_div_matches_python() {
        assert_eq!(floor_div(7, 2), 3);
        assert_eq!(floor_div(-7, 2), -4);
        assert_eq!(floor_div(7, -2), -4);
        assert_eq!(floor_div(-7, -2), 3);
    }

    #[test]
    fn floor_mod_sign_follows_divisor() {
        assert_eq!(floor_mod(7, 2), 1);
        assert_eq!(floor_mod(-7, 2), 1);
        assert_eq!(floor_mod(7, -2), -1);
        assert_eq!(floor_mod(-7, -2), -1);
    }

    #[test]
    fn float_repr_adds_point_zero() {
        assert_eq!(float_repr(2.0), "2.0");
        assert_eq!(float_repr(2.5), "2.5");
        assert_eq!(float_repr(0.06), "0.06");
    }

    #[test]
    fn float_repr_matches_python_exponents() {
        assert_eq!(float_repr(1e20), "1e+20");
        assert_eq!(float_repr(1e16), "1e+16");
        assert_eq!(float_repr(1e-5), "1e-05");
        assert_eq!(float_repr(1e-4), "0.0001");
        assert_eq!(float_repr(-0.0), "-0.0");
        assert_eq!(float_repr(f64::INFINITY), "inf");
        assert_eq!(float_repr(f64::NAN), "nan");
    }

    #[test]
    fn truthiness() {
        assert!(!truthy(&Value::Null));
        assert!(!truthy(&Value::Int(0)));
        assert!(!truthy(&Value::Float(0.0)));
        assert!(!truthy(&Value::Bool(false)));
        assert!(truthy(&Value::Int(1)));
        assert!(truthy(&Value::Bool(true)));
    }

    #[test]
    fn int_division_yields_float() {
        let v = binary(DIV, &Value::Int(7), &Value::Int(2)).unwrap();
        assert!(matches!(v, Value::Float(f) if (f - 3.5).abs() < 1e-9));
    }

    #[test]
    fn mixed_int_float_equality() {
        let v = binary(EQ, &Value::Int(1), &Value::Float(1.0)).unwrap();
        assert!(matches!(v, Value::Bool(true)));
        // Bool is not a number: true == 1 is false.
        let v = binary(EQ, &Value::Bool(true), &Value::Int(1)).unwrap();
        assert!(matches!(v, Value::Bool(false)));
    }

    fn big(text: &str) -> Value {
        Value::Big(Rc::new(text.parse::<BigInt>().unwrap()))
    }

    #[test]
    fn integer_overflow_promotes_to_big() {
        let v = binary(ADD, &Value::Int(i64::MAX), &Value::Int(1)).unwrap();
        assert_eq!(display(&v), "9223372036854775808");
        let v = binary(MUL, &big("9223372036854775808"), &Value::Int(3)).unwrap();
        assert_eq!(display(&v), "27670116110564327424");
        let v = binary(SUB, &Value::Int(i64::MIN), &Value::Int(1)).unwrap();
        assert_eq!(display(&v), "-9223372036854775809");
    }

    #[test]
    fn big_floor_division_and_modulo() {
        let a = big("1267650600228229401496703205376"); // 2**100
        assert_eq!(
            display(&binary(FLOORDIV, &a, &Value::Int(3)).unwrap()),
            "422550200076076467165567735125"
        );
        assert_eq!(display(&binary(MOD, &a, &Value::Int(7)).unwrap()), "2");
        let negative = big("-1267650600228229401496703205377");
        assert_eq!(
            display(&binary(FLOORDIV, &negative, &Value::Int(3)).unwrap()),
            "-422550200076076467165567735126"
        );
        assert_eq!(
            display(&binary(MOD, &negative, &Value::Int(3)).unwrap()),
            "1"
        );
    }

    #[test]
    fn big_comparison_is_exact() {
        let two_pow_53 = big("9007199254740993"); // 2**53 + 1
        let as_float = Value::Float(9007199254740992.0);
        assert!(matches!(
            binary(EQ, &two_pow_53, &as_float).unwrap(),
            Value::Bool(false)
        ));
        assert!(matches!(
            binary(GT, &two_pow_53, &as_float).unwrap(),
            Value::Bool(true)
        ));
        assert!(matches!(
            binary(LT, &as_float, &two_pow_53).unwrap(),
            Value::Bool(true)
        ));
    }

    #[test]
    fn nan_ordering_is_false() {
        let nan = Value::Float(f64::NAN);
        for op in [LT, LE, GT, GE] {
            let v = binary(op, &nan, &Value::Int(1)).unwrap();
            assert!(matches!(v, Value::Bool(false)));
        }
    }

    #[test]
    fn big_unary_operators() {
        let v = unary(NEG, &big("9223372036854775808")).unwrap();
        assert_eq!(display(&v), "-9223372036854775808");
        // i64::MIN negates into a big int instead of erroring.
        let v = unary(NEG, &Value::Int(i64::MIN)).unwrap();
        assert_eq!(display(&v), "9223372036854775808");
        let v = unary(INVERT, &big("9223372036854775808")).unwrap();
        assert_eq!(display(&v), "-9223372036854775809");
    }

    #[test]
    fn range_rejects_big_arguments() {
        assert!(int_arg(&big("9223372036854775808")).is_err());
        assert_eq!(int_arg(&Value::Int(3)).unwrap(), 3);
    }
}
