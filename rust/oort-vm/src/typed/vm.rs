//! Typed register VM: global resolution, frame pool and the opcode loop.

use std::cell::{Cell, RefCell};
use std::cmp::Ordering;
use std::collections::HashMap;
use std::rc::Rc;

use num_bigint::BigInt;
use num_integer::Integer;
use num_traits::{ToPrimitive, Zero};

use crate::obc::{annotate_error, Constant};
use crate::vm::Value;

use super::opcodes::*;
use super::value::{
    adt_constructor, as_bool, as_float, as_index, as_int, as_str, closure_slot, constant_value,
    dict_set, display_typed, get_item, guard, iterator_next, mixed_cmp, normalize_index,
    open_iterator, set_insert, sort_typed_values, to_value, typed_contains, typed_equal,
    typed_list_cmp, typed_list_concat, typed_set_op, typed_set_relation, typed_slice, unwrap_cell,
    TypedAdt, TypedClosure, TypedNative, TypedValue,
};
use super::{TResult, TypedAdtDecl, TypedModule, TypedProto, TypedType};

pub struct TypedVm {
    functions: Vec<ResolvedProto>,
    main: ResolvedProto,
    adt_decls: Vec<TypedAdtDecl>,
    pool: FramePool,
    globals: GlobalTable,
    trace: bool,
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

/// A resolved `LOAD_G` target. Values are cloned out of their slot; caching
/// them is sound because `STORE_G` bumps the version, forcing a re-resolve.
#[derive(Clone)]
enum TypedGlobal {
    Function(usize),
    Native(TypedNative),
    Value(TypedValue),
}

/// A cached `LOAD_G` target. The version makes invalidation lazy: a globals
/// write bumps `GlobalTable::version`, and the next load refreshes the entry.
#[derive(Clone)]
struct CachedGlobal {
    version: u64,
    target: TypedGlobal,
}

enum GlobalSlot {
    Function(usize),
    Native(TypedNative),
    /// A top-level val/var binding written by `STORE_G`; `main` initializes
    /// these in module order, so reads before the store are "unknown name".
    Value(RefCell<TypedValue>),
}

/// Runtime global bindings: module functions, natives and top-level values.
/// Interior mutability keeps `execute`'s `&GlobalTable` while `STORE_G`
/// writes; the version hook invalidates cached `LOAD_G` targets.
struct GlobalTable {
    version: Cell<u64>,
    bindings: RefCell<HashMap<String, GlobalSlot>>,
}

impl GlobalTable {
    fn from_module(module: &TypedModule) -> Self {
        let mut bindings: HashMap<String, GlobalSlot> = module
            .functions
            .iter()
            .enumerate()
            .map(|(index, proto)| (proto.name.clone(), GlobalSlot::Function(index)))
            .collect();
        // A user function named `print` keeps precedence over the native.
        bindings
            .entry("print".to_string())
            .or_insert(GlobalSlot::Native(TypedNative::Print));
        bindings
            .entry("len".to_string())
            .or_insert(GlobalSlot::Native(TypedNative::Len));
        bindings
            .entry("sorted".to_string())
            .or_insert(GlobalSlot::Native(TypedNative::Sorted));
        GlobalTable {
            version: Cell::new(0),
            bindings: RefCell::new(bindings),
        }
    }

    fn version(&self) -> u64 {
        self.version.get()
    }

    fn lookup(&self, name: &str) -> Option<TypedGlobal> {
        match self.bindings.borrow().get(name) {
            Some(GlobalSlot::Function(index)) => Some(TypedGlobal::Function(*index)),
            Some(GlobalSlot::Native(native)) => Some(TypedGlobal::Native(*native)),
            Some(GlobalSlot::Value(value)) => Some(TypedGlobal::Value(value.borrow().clone())),
            None => None,
        }
    }

    /// `STORE_G`: define or overwrite a global, then invalidate caches.
    fn store(&self, name: &str, value: TypedValue) {
        self.bindings
            .borrow_mut()
            .insert(name.to_string(), GlobalSlot::Value(RefCell::new(value)));
        self.invalidate();
    }

    fn invalidate(&self) {
        self.version.set(self.version.get().wrapping_add(1));
    }
}

/// A proto plus its `LOAD_G` cache, keyed by constant-pool index.
struct ResolvedProto {
    proto: Rc<TypedProto>,
    globals: Vec<RefCell<Option<CachedGlobal>>>,
}

fn resolve_globals(
    proto: &TypedProto,
    globals: &GlobalTable,
) -> Vec<RefCell<Option<CachedGlobal>>> {
    proto
        .constants
        .iter()
        .map(|constant| match constant {
            Constant::Str(name) => match globals.lookup(name) {
                Some(target) => RefCell::new(Some(CachedGlobal {
                    version: globals.version(),
                    target,
                })),
                None => RefCell::new(None),
            },
            _ => RefCell::new(None),
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
    if let Some(cached) = entry.borrow().as_ref() {
        if cached.version == globals.version() {
            return Ok(cached.target.clone());
        }
    }
    let name = match resolved.proto.constants.get(index) {
        Some(Constant::Str(name)) => name.as_ref(),
        _ => return Err("invalid global name constant".into()),
    };
    let target = globals
        .lookup(name)
        .ok_or_else(|| format!("unknown name '{name}'"))?;
    *entry.borrow_mut() = Some(CachedGlobal {
        version: globals.version(),
        target: target.clone(),
    });
    Ok(target)
}

impl TypedVm {
    pub fn new(module: TypedModule) -> Self {
        let globals = GlobalTable::from_module(&module);
        let adt_decls = module.adt_decls.clone();
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
            adt_decls,
            pool: FramePool::new(),
            globals,
            trace: false,
        }
    }

    /// Enable or disable the per-instruction trace on stderr.
    pub fn set_trace(&mut self, trace: bool) {
        self.trace = trace;
    }

    /// Bump the globals version; cached `LOAD_G` targets refresh lazily.
    pub fn invalidate_globals(&mut self) {
        self.globals.invalidate();
    }

    pub fn run_main(&mut self) -> TResult<Value> {
        let functions = &self.functions;
        let main = &self.main;
        let globals = &self.globals;
        let adt_decls = &self.adt_decls;
        let trace = self.trace;
        let pool = &mut self.pool;
        let mut frame = pool.acquire(main.proto.register_count as usize);
        let result = if trace {
            execute::<true>(main, functions, globals, adt_decls, pool, &mut frame, None)
        } else {
            execute::<false>(main, functions, globals, adt_decls, pool, &mut frame, None)
        };
        pool.release(frame);
        result.and_then(to_value)
    }
}

/// Outcome of one instruction. Jumps and returns carry their target/value so
/// the dispatch loop can handle control flow outside the per-instruction body,
/// where `?` can attach the current source position to any error.
enum Flow {
    Next,
    Jump(usize),
    Return(TypedValue),
}

/// Run one typed proto to completion.
///
/// Register layout is fixed by the compiler: parameters and locals occupy
/// their HIR slots, call arguments are moved into a contiguous window at the
/// callee register, and the result lands in its own register. Jumps use
/// absolute word indices. `closure` is the executing closure, if any; named
/// functions and main pass `None`.
///
/// Any error raised while executing a word is annotated with that word's
/// source position; the trace grows as the error unwinds through callers.
fn execute<const TRACE: bool>(
    resolved: &ResolvedProto,
    functions: &[ResolvedProto],
    globals: &GlobalTable,
    adt_decls: &[TypedAdtDecl],
    pool: &mut FramePool,
    registers: &mut [TypedValue],
    closure: Option<&Rc<TypedClosure>>,
) -> TResult<TypedValue> {
    let proto = &resolved.proto;
    // Frame entry: share the slots captured by lambdas. Parameters already
    // hold their argument values; wrapping keeps those values observable
    // through the cell.
    for &slot in &proto.cells {
        let index = slot as usize;
        if index < registers.len() {
            registers[index] = TypedValue::Cell(Rc::new(RefCell::new(registers[index].clone())));
        }
    }
    let mut pc = 0usize;
    while pc < proto.code.len() {
        let word = proto.code[pc];
        let op = word >> 24;
        let a = ((word >> 16) & 0xFF) as usize;
        let b = ((word >> 8) & 0xFF) as usize;
        let c = (word & 0xFF) as usize;
        let bx = (word & 0xFFFF) as usize;

        let step = (|| -> TResult<Flow> {
            match op {
                LOAD_K => {
                    registers[a] = constant_value(&proto.constants[bx])?;
                }
                LOAD_L => {
                    // Cell slots read transparently; the value itself is copied.
                    registers[a] = unwrap_cell(&registers[b]).into_owned();
                }
                STORE_L => {
                    // Cell slots write through to the shared cell; plain slots
                    // are ordinary register writes.
                    if let TypedValue::Cell(cell) = &registers[a] {
                        *cell.borrow_mut() = unwrap_cell(&registers[b]).into_owned();
                    } else {
                        registers[a] = registers[b].clone();
                    }
                }
                LOAD_G => {
                    registers[a] = match resolve_global(resolved, globals, bx)? {
                        TypedGlobal::Function(index) => TypedValue::Function(index),
                        TypedGlobal::Native(native) => TypedValue::Native(native),
                        TypedGlobal::Value(value) => value,
                    };
                }
                STORE_G => {
                    // A=source register, Bx=name constant (mirrors LOAD_G).
                    let name = match proto.constants.get(bx) {
                        Some(Constant::Str(name)) => name.as_ref(),
                        _ => return Err("invalid global name constant".into()),
                    };
                    globals.store(name, registers[a].clone());
                }
                DEF_FUN => {}
                MK_FUN => {
                    let index = bx as usize;
                    if index >= functions.len() {
                        return Err("typed MK_FUN index out of range".into());
                    }
                    registers[a] = TypedValue::Function(index);
                }
                MK_CLOSURE => {
                    let index = bx as usize;
                    if index >= functions.len() {
                        return Err("typed MK_CLOSURE index out of range".into());
                    }
                    // Snapshot the whole frame: captured slots are already cells,
                    // so the snapshot shares them; other slots are inert copies.
                    registers[a] = TypedValue::Closure(Rc::new(TypedClosure {
                        index,
                        snapshot: registers.to_vec(),
                        parent: closure.cloned(),
                    }));
                }
                LOAD_OUTER => {
                    registers[a] = unwrap_cell(closure_slot(closure, b, c)?).into_owned();
                }
                STORE_OUTER => {
                    // Operands: A=depth, B=slot, C=source register.
                    let target = closure_slot(closure, a, b)?;
                    match target {
                        TypedValue::Cell(cell) => *cell.borrow_mut() = registers[c].clone(),
                        _ => return Err("typed closure write target is not a shared cell".into()),
                    }
                }
                FRESH_CELL => {
                    // Loop entry: give each iteration its own cell so closures
                    // created earlier keep the binding they captured.
                    registers[a] = TypedValue::Cell(Rc::new(RefCell::new(TypedValue::Unit)));
                }
                MOVE => {
                    registers[a] = registers[b].clone();
                }
                ADD_I | SUB_I | MUL_I | FLOORDIV_I | MOD_I => {
                    let left = as_int(&registers[b])?;
                    let right = as_int(&registers[c])?;
                    let result = match op {
                        ADD_I => left + right,
                        SUB_I => left - right,
                        MUL_I => left * right,
                        FLOORDIV_I => {
                            if right.is_zero() {
                                return Err("division or modulo by zero".into());
                            }
                            left.div_floor(right)
                        }
                        _ => {
                            if right.is_zero() {
                                return Err("division or modulo by zero".into());
                            }
                            left.mod_floor(right)
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
                        -value.clone()
                    } else {
                        value.clone()
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
                        TypedValue::Int(i) => i.to_f64().ok_or("integer is too large for Float")?,
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
                NEW_ADT => {
                    let (_decl_index, ctor_index, ctor) = adt_constructor(adt_decls, b as u16)?;
                    let payload: Vec<TypedValue> = if ctor.1 == 0 {
                        Vec::new()
                    } else {
                        registers[a..a + ctor.1 as usize].to_vec()
                    };
                    let type_id = proto
                        .register_types
                        .get(c)
                        .copied()
                        .flatten()
                        .ok_or_else(|| "typed ADT target has no static type".to_string())?;
                    let type_ = proto
                        .types
                        .get(type_id as usize)
                        .cloned()
                        .ok_or_else(|| "typed ADT target type id out of range".to_string())?;
                    if !matches!(type_, TypedType::Adt(_, _)) {
                        return Err("typed ADT target is not an ADT type".into());
                    }
                    registers[c] = TypedValue::Adt(Rc::new(TypedAdt {
                        type_,
                        variant: ctor_index,
                        variant_name: Rc::from(ctor.0.as_str()),
                        payload: payload.into_boxed_slice(),
                    }));
                }
                ADT_TAG => {
                    let TypedValue::Adt(value) = &registers[b] else {
                        return Err("typed ADT_TAG expects an ADT".into());
                    };
                    registers[a] = TypedValue::Int(BigInt::from(value.variant));
                }
                ADT_FIELD => {
                    let TypedValue::Adt(value) = &registers[b] else {
                        return Err("typed ADT_FIELD expects an ADT".into());
                    };
                    let field = value
                        .payload
                        .get(c)
                        .ok_or_else(|| "typed ADT field index out of range".to_string())?;
                    registers[a] = field.clone();
                }
                TUPLE_ITEM => {
                    let TypedValue::Tuple(items) = &registers[b] else {
                        return Err("typed TUPLE_ITEM expects a Tuple".into());
                    };
                    let item = items
                        .get(c)
                        .ok_or_else(|| "typed tuple index out of range".to_string())?;
                    registers[a] = item.clone();
                }
                NEW_SET => {
                    let mut items = Vec::with_capacity(b);
                    for value in &registers[a..a + b] {
                        set_insert(&mut items, value.clone())?;
                    }
                    registers[c] = TypedValue::Set(Rc::new(RefCell::new(items)));
                }
                NEW_DICT => {
                    let mut entries = Vec::with_capacity(b);
                    for index in 0..b {
                        let key = registers[a + 2 * index].clone();
                        let value = registers[a + 2 * index + 1].clone();
                        dict_set(&mut entries, key, value)?;
                    }
                    registers[c] = TypedValue::Dict(Rc::new(RefCell::new(entries)));
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
                    if let TypedValue::List(items) = &registers[a] {
                        let index = as_index(&registers[b])?;
                        let mut items = items.borrow_mut();
                        let position = normalize_index(index, items.len())?;
                        items[position] = registers[c].clone();
                    } else if let TypedValue::Dict(entries) = &registers[a] {
                        let mut entries = entries.borrow_mut();
                        dict_set(&mut entries, registers[b].clone(), registers[c].clone())?;
                    } else {
                        return Err("typed SET_ITEM expects a List or Dict".into());
                    }
                }
                CONTAINS => {
                    registers[a] = TypedValue::Bool(typed_contains(&registers[b], &registers[c])?);
                }
                SLICE => {
                    let start = if b & 1 != 0 {
                        Some(&registers[a + 1])
                    } else {
                        None
                    };
                    let stop = if b & 2 != 0 {
                        Some(&registers[a + 2])
                    } else {
                        None
                    };
                    registers[c] = typed_slice(&registers[a], start, stop)?;
                }
                SET_UNION | SET_INTERSECT | SET_DIFFERENCE | SET_SYMMETRIC => {
                    registers[a] = typed_set_op(op, &registers[b], &registers[c])?;
                }
                SET_SUBSET | SET_PROPER_SUBSET | SET_SUPERSET | SET_PROPER_SUPERSET => {
                    registers[a] =
                        TypedValue::Bool(typed_set_relation(op, &registers[b], &registers[c])?);
                }
                CMP_LIST => {
                    registers[a] = TypedValue::Int(BigInt::from(typed_list_cmp(
                        &registers[b],
                        &registers[c],
                    )?));
                }
                LIST_CONCAT => {
                    registers[a] = typed_list_concat(&registers[b], &registers[c])?;
                }
                EQ_LIST | NE_LIST | EQ_TUPLE | NE_TUPLE | EQ_SET | NE_SET | EQ_DICT | NE_DICT
                | EQ_ADT | NE_ADT => {
                    let mut equal = typed_equal(&registers[b], &registers[c])?;
                    if matches!(op, NE_LIST | NE_TUPLE | NE_SET | NE_DICT | NE_ADT) {
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
                    return Ok(Flow::Jump(bx));
                }
                JMP_FALSE => {
                    if !as_bool(&registers[a])? {
                        return Ok(Flow::Jump(bx));
                    }
                }
                JMP_TRUE => {
                    if as_bool(&registers[a])? {
                        return Ok(Flow::Jump(bx));
                    }
                }
                CALL => {
                    let callee = registers[a].clone();
                    let result = call::<TRACE>(
                        functions,
                        globals,
                        adt_decls,
                        pool,
                        callee,
                        &registers[a + 1..a + 1 + b],
                    )?;
                    registers[c] = result;
                }
                RET => {
                    return Ok(Flow::Return(registers[a].clone()));
                }
                _ => return Err(format!("unknown typed opcode {op}")),
            }
            Ok(Flow::Next)
        })();
        match step {
            Ok(Flow::Next) => {
                if TRACE {
                    let mut text = trace_text(proto, pc, op, a, b, c, bx);
                    if let Some(dest) = trace_dest(op, a, c) {
                        if let Some(value) = registers.get(dest) {
                            text.push_str(&format!(" -> R{dest}={}", display_typed(value)));
                        }
                    }
                    eprintln!("{text}");
                }
                pc += 1;
            }
            Ok(Flow::Jump(target)) => {
                if TRACE {
                    eprintln!("{} -> pc={target}", trace_text(proto, pc, op, a, b, c, bx));
                }
                pc = target;
            }
            Ok(Flow::Return(value)) => {
                if TRACE {
                    eprintln!(
                        "{} -> ret {}",
                        trace_text(proto, pc, op, a, b, c, bx),
                        display_typed(&value)
                    );
                }
                return Ok(value);
            }
            Err(error) => {
                let pos = proto.positions.get(pc).copied();
                return Err(annotate_error(&proto.name, &proto.filename, pos, error));
            }
        }
    }
    Err(annotate_error(
        &proto.name,
        &proto.filename,
        None,
        format!("typed function '{}' fell off the end", proto.name),
    ))
}

/// One trace line: decoded operands plus the instruction's source line.
fn trace_text(
    proto: &TypedProto,
    pc: usize,
    op: u32,
    a: usize,
    b: usize,
    c: usize,
    bx: usize,
) -> String {
    let name = match super::opcodes::name(op) {
        Some(name) => name.to_string(),
        None => format!("OP{op}"),
    };
    let line = proto.positions.get(pc).map_or(0, |pos| pos.line);
    format!(
        "[{}] {pc:04}  {name} a={a} b={b} c={c} bx={bx}  ; line {line}",
        proto.name
    )
}

/// Register that receives an instruction's result, when it has one. Operand
/// layouts differ per opcode: calls and container builders write `C`, most
/// others write `A`, and control flow writes no register.
fn trace_dest(op: u32, a: usize, c: usize) -> Option<usize> {
    match op {
        JMP | JMP_FALSE | JMP_TRUE | RET | STORE_G | STORE_OUTER => None,
        CALL | NEW_LIST | NEW_TUPLE | NEW_SET | NEW_DICT | NEW_ADT | SLICE => Some(c),
        _ => Some(a),
    }
}

fn call<const TRACE: bool>(
    functions: &[ResolvedProto],
    globals: &GlobalTable,
    adt_decls: &[TypedAdtDecl],
    pool: &mut FramePool,
    callee: TypedValue,
    arguments: &[TypedValue],
) -> TResult<TypedValue> {
    match callee {
        TypedValue::Closure(closure) => {
            let resolved = functions
                .get(closure.index)
                .ok_or("invalid typed function index")?;
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
            let result = execute::<TRACE>(
                resolved,
                functions,
                globals,
                adt_decls,
                pool,
                &mut frame,
                Some(&closure),
            );
            pool.release(frame);
            result
        }
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
            let result = execute::<TRACE>(
                resolved, functions, globals, adt_decls, pool, &mut frame, None,
            );
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
                TypedValue::Str(s) => Ok(TypedValue::Int(BigInt::from(s.chars().count()))),
                TypedValue::List(items) => Ok(TypedValue::Int(BigInt::from(items.borrow().len()))),
                TypedValue::Tuple(items) => Ok(TypedValue::Int(BigInt::from(items.len()))),
                TypedValue::Set(items) => Ok(TypedValue::Int(BigInt::from(items.borrow().len()))),
                TypedValue::Dict(entries) => {
                    Ok(TypedValue::Int(BigInt::from(entries.borrow().len())))
                }
                _ => Err("len expects a String, List or Tuple in the typed subset".into()),
            }
        }
        TypedValue::Native(TypedNative::Sorted) => {
            if arguments.len() != 1 {
                return Err("sorted expects exactly one argument".into());
            }
            match &arguments[0] {
                TypedValue::List(items) => {
                    let mut values = items.borrow().clone();
                    sort_typed_values(&mut values)?;
                    Ok(TypedValue::List(Rc::new(RefCell::new(values))))
                }
                _ => Err("sorted expects a List".into()),
            }
        }
        _ => Err("typed bytecode call target is not callable".into()),
    }
}
#[cfg(test)]
mod tests {
    use super::*;

    use crate::typed::TypedType;

    fn int(value: i64) -> TypedValue {
        TypedValue::Int(BigInt::from(value))
    }

    #[test]
    fn resolves_globals_once_per_proto() {
        let proto = TypedProto {
            cells: vec![],
            name: "test".into(),
            is_main: false,
            register_count: 0,
            types: vec![],
            register_types: vec![],
            param_types: vec![],
            ret_type: TypedType::Unit,
            code: vec![],
            positions: vec![],
            filename: String::new(),
            constants: vec![
                Constant::Str(Rc::from("f")),
                Constant::Str(Rc::from("print")),
                Constant::Str(Rc::from("missing")),
            ],
        };
        let globals = GlobalTable {
            version: Cell::new(0),
            bindings: RefCell::new(HashMap::from([
                ("f".to_string(), GlobalSlot::Function(0)),
                ("print".to_string(), GlobalSlot::Native(TypedNative::Print)),
            ])),
        };

        let cells = resolve_globals(&proto, &globals);
        assert!(matches!(
            cells[0].borrow().as_ref().unwrap().target,
            TypedGlobal::Function(0)
        ));
        assert!(matches!(
            cells[1].borrow().as_ref().unwrap().target,
            TypedGlobal::Native(TypedNative::Print)
        ));
        assert!(cells[2].borrow().is_none());
    }

    #[test]
    fn cached_globals_refresh_after_version_bump() {
        let proto = TypedProto {
            cells: vec![],
            name: "g".into(),
            is_main: false,
            register_count: 0,
            types: vec![],
            register_types: vec![],
            param_types: vec![],
            ret_type: TypedType::Unit,
            code: vec![],
            positions: vec![],
            filename: String::new(),
            constants: vec![Constant::Str(Rc::from("f"))],
        };
        let resolved = ResolvedProto {
            proto: Rc::new(proto),
            globals: vec![RefCell::new(None)],
        };
        let globals = GlobalTable {
            version: Cell::new(0),
            bindings: RefCell::new(HashMap::from([("f".to_string(), GlobalSlot::Function(0))])),
        };

        assert!(matches!(
            resolve_global(&resolved, &globals, 0).unwrap(),
            TypedGlobal::Function(0)
        ));

        globals.store("f", TypedValue::Int(BigInt::from(7)));
        assert!(matches!(
            resolve_global(&resolved, &globals, 0).unwrap(),
            TypedGlobal::Value(_)
        ));
        assert_eq!(globals.version(), 1);
    }

    #[test]
    fn store_global_then_load_roundtrip() {
        let globals = GlobalTable::from_module(&TypedModule {
            functions: vec![],
            main: Rc::new(TypedProto {
                cells: vec![],
                name: "<main>".into(),
                is_main: true,
                register_count: 0,
                types: vec![],
                register_types: vec![],
                param_types: vec![],
                ret_type: TypedType::Unit,
                code: vec![],
                positions: vec![],
                filename: String::new(),
                constants: vec![],
            }),
            adt_decls: vec![],
        });
        globals.store("answer", TypedValue::Int(BigInt::from(42)));
        match globals.lookup("answer") {
            Some(TypedGlobal::Value(TypedValue::Int(i))) => {
                assert_eq!(i, BigInt::from(42));
            }
            Some(TypedGlobal::Value(_)) => panic!("unexpected stored value"),
            _ => panic!("expected a value slot"),
        }
    }

    #[test]
    fn runtime_errors_carry_source_position() {
        // ADD_I over two untouched registers (Unit) fails in `as_int`; the
        // dispatch loop must attach the word's source position to the error.
        let proto = TypedProto {
            name: "f".into(),
            is_main: false,
            register_count: 3,
            types: vec![],
            register_types: vec![],
            param_types: vec![],
            ret_type: TypedType::Unit,
            cells: vec![],
            code: vec![(ADD_I << 24) | (0 << 16) | (1 << 8) | 2],
            constants: vec![],
            positions: vec![crate::obc::SourcePos { line: 7, column: 4 }],
            filename: "main.ort".into(),
        };
        let resolved = ResolvedProto {
            proto: Rc::new(proto),
            globals: vec![],
        };
        let globals = GlobalTable {
            version: Cell::new(0),
            bindings: RefCell::new(HashMap::new()),
        };
        let mut pool = FramePool::new();
        let mut frame = vec![TypedValue::Unit; 3];
        let error =
            match execute::<false>(&resolved, &[], &globals, &[], &mut pool, &mut frame, None) {
                Err(error) => error,
                Ok(_) => panic!("expected a runtime error"),
            };
        assert!(error.starts_with("main.ort:7:5: error: "), "{error}");
    }

    #[test]
    fn frame_pool_reuses_and_resets_frames() {
        let mut pool = FramePool::new();
        let mut first = pool.acquire(4);
        first[0] = int(7);
        pool.release(first);

        let reused = pool.acquire(4);
        assert_eq!(reused.len(), 4);
        assert!(matches!(reused[0], TypedValue::Unit));

        let larger = pool.acquire(8);
        assert_eq!(larger.len(), 8);
    }
}
