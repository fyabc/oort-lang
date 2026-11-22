//! Spike register VM for type-erased Oort bytecode. Phase 0 subset: enough to
//! run the fib/loop/methods benchmarks and a handful of differential cases.
//! Semantics mirror `runtime/bytecode_vm.py` (frame layout, calling convention,
//! numeric rules). Unsupported opcodes fail explicitly, never silently.

use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::Rc;
use std::time::Instant;

use crate::obc::{Constant, Module, Proto};

pub type Globals = HashMap<String, Value>;

#[derive(Clone)]
pub enum Value {
    Null,
    Bool(bool),
    Int(i64),
    Float(f64),
    Str(Rc<str>),
    List(Rc<RefCell<Vec<Value>>>),
    Tuple(Rc<[Value]>),
    Set(Rc<RefCell<Vec<Value>>>),
    Dict(Rc<RefCell<Vec<(Value, Value)>>>),
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
        Value::Float(f) => *f != 0.0,
        Value::Str(s) => !s.is_empty(),
        Value::List(l) => !l.borrow().is_empty(),
        Value::Set(items) => !items.borrow().is_empty(),
        Value::Dict(entries) => !entries.borrow().is_empty(),
        _ => true, // instances, types, callables are always truthy
    }
}

fn as_f64(v: &Value) -> Option<f64> {
    match v {
        Value::Int(i) => Some(*i as f64),
        Value::Float(f) => Some(*f),
        _ => None,
    }
}

fn type_name(v: &Value) -> &'static str {
    match v {
        Value::Null => "Null",
        Value::Bool(_) => "Bool",
        Value::Int(_) => "Int",
        Value::Float(_) => "Float",
        Value::Str(_) => "String",
        Value::List(_) => "List",
        Value::Tuple(_) => "Tuple",
        Value::Set(_) => "Set",
        Value::Dict(_) => "Dict",
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
            _ => match (as_f64(lhs), as_f64(rhs)) {
                // Bool is not a number: as_f64 returns None for Bool.
                (Some(a), Some(b)) => a == b,
                _ => false,
            },
        };
        return Ok(Value::Bool(if op == EQ { eq } else { !eq }));
    }

    // Ordering: numeric (Int/Float) or String.
    if matches!(op, LT | LE | GT | GE) {
        let ord = match (lhs, rhs) {
            (Value::Str(a), Value::Str(b)) => a.cmp(b),
            _ => match (as_f64(lhs), as_f64(rhs)) {
                (Some(a), Some(b)) => a.partial_cmp(&b).unwrap_or(std::cmp::Ordering::Equal),
                _ => {
                    return Err(format!(
                        "'{}' and '{}' are not orderable",
                        type_name(lhs),
                        type_name(rhs)
                    ))
                }
            },
        };
        let result = match op {
            LT => ord == std::cmp::Ordering::Less,
            LE => ord != std::cmp::Ordering::Greater,
            GT => ord == std::cmp::Ordering::Greater,
            _ => ord != std::cmp::Ordering::Less,
        };
        return Ok(Value::Bool(result));
    }

    // Arithmetic.
    if let (Value::Int(a), Value::Int(b)) = (lhs, rhs) {
        let (a, b) = (*a, *b);
        return Ok(match op {
            ADD => Value::Int(a.checked_add(b).ok_or("integer overflow")?),
            SUB => Value::Int(a.checked_sub(b).ok_or("integer overflow")?),
            MUL => Value::Int(a.checked_mul(b).ok_or("integer overflow")?),
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
                Value::Int(floor_div(a, b))
            }
            MOD => {
                if b == 0 {
                    return Err("modulo by zero".into());
                }
                Value::Int(floor_mod(a, b))
            }
            _ => return Err(format!("unsupported integer operator {op}")),
        });
    }
    if let (Some(a), Some(b)) = (as_f64(lhs), as_f64(rhs)) {
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
            FLOORDIV => Value::Float((a / b).floor()),
            MOD => Value::Float(a - b * (a / b).floor()),
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
            Value::Int(i) => Ok(Value::Int(i.checked_neg().ok_or("integer overflow")?)),
            Value::Float(f) => Ok(Value::Float(-f)),
            _ => Err(format!(
                "Type '{}' does not support unary '-'",
                type_name(v)
            )),
        },
        POS => match v {
            Value::Int(_) | Value::Float(_) => Ok(v.clone()),
            _ => Err(format!(
                "Type '{}' does not support unary '+'",
                type_name(v)
            )),
        },
        INVERT => match v {
            Value::Int(i) => Ok(Value::Int(!i)),
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
}
