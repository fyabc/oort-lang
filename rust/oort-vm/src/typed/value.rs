//! Typed runtime values, display/equality and opcode helpers.

use std::cell::RefCell;
use std::cmp::Ordering;
use std::rc::Rc;

use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::ToPrimitive;

use crate::obc::Constant;
use crate::vm::{float_repr, Value};

use super::opcodes::{
    SET_DIFFERENCE, SET_INTERSECT, SET_PROPER_SUBSET, SET_PROPER_SUPERSET, SET_SUBSET, SET_UNION,
};
use super::{TResult, TypedAdtDecl, TypedType};

///
/// `Function` is a plain module function index; `Closure` carries a parent
/// chain. `Cell` is an implementation detail: it lives only in frame registers
/// and closure snapshots for slots shared with lambdas, and every read path
/// (`LOAD_L`, `LOAD_OUTER`, display, equality) unwraps it, so user-visible
/// values are never cells.
#[derive(Clone)]
pub(crate) enum TypedValue {
    Unit,
    Bool(bool),
    Int(BigInt),
    Float(f64),
    Str(Rc<str>),
    List(Rc<RefCell<Vec<TypedValue>>>),
    Tuple(Rc<[TypedValue]>),
    Set(Rc<RefCell<Vec<TypedValue>>>),
    Dict(Rc<RefCell<Vec<(TypedValue, TypedValue)>>>),
    Adt(Rc<TypedAdt>),
    Iterator(Rc<RefCell<TypedIterator>>),
    Function(usize),
    Closure(Rc<TypedClosure>),
    Cell(Rc<RefCell<TypedValue>>),
    Native(TypedNative),
}

/// A capturing lambda: its function index plus a creation-time frame
/// snapshot and the enclosing closure (if any).
///
/// Captured slots hold `Cell`s in the snapshot, so reads and writes through
/// `LOAD_OUTER`/`STORE_OUTER` are shared with the creating frame (reference
/// semantics). The parent chain exists only to reach frames further out;
/// depth 1 refers to this closure's own snapshot.
pub(crate) struct TypedClosure {
    pub(crate) index: usize,
    pub(crate) snapshot: Vec<TypedValue>,
    pub(crate) parent: Option<Rc<TypedClosure>>,
}

pub(crate) struct TypedAdt {
    pub(crate) type_: TypedType,
    pub(crate) variant: u16,
    pub(crate) variant_name: Rc<str>,
    pub(crate) payload: Box<[TypedValue]>,
}

/// Snapshot iterator over a List, Tuple, Set, Dict keys or String.
pub(crate) struct TypedIterator {
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
pub(crate) enum TypedNative {
    Print,
    Len,
    Sorted,
}

pub(crate) fn display_typed(value: &TypedValue) -> String {
    let value = unwrap_cell(value);
    match &*value {
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
        TypedValue::Set(items) => {
            let items = items.borrow();
            if items.is_empty() {
                "{.}".into()
            } else {
                let parts: Vec<String> = items.iter().map(display_typed).collect();
                format!("{{. {} .}}", parts.join(", "))
            }
        }
        TypedValue::Dict(entries) => {
            let entries = entries.borrow();
            if entries.is_empty() {
                "{:}".into()
            } else {
                let parts: Vec<String> = entries
                    .iter()
                    .map(|(key, value)| format!("{}: {}", display_typed(key), display_typed(value)))
                    .collect();
                format!("{{: {} :}}", parts.join(", "))
            }
        }
        TypedValue::Adt(value) => {
            if value.payload.is_empty() {
                value.variant_name.to_string()
            } else {
                let parts: Vec<String> = value.payload.iter().map(display_typed).collect();
                format!("{}({})", value.variant_name, parts.join(", "))
            }
        }
        TypedValue::Iterator(_) => "<iterator>".into(),
        TypedValue::Function(_)
        | TypedValue::Closure(_)
        | TypedValue::Cell(_)
        | TypedValue::Native(_) => "<function>".into(),
    }
}

pub(crate) fn to_value(value: TypedValue) -> TResult<Value> {
    typed_to_value(&value)
}

fn typed_to_value(value: &TypedValue) -> TResult<Value> {
    Ok(match value {
        TypedValue::Unit => Value::Null,
        TypedValue::Bool(b) => Value::Bool(*b),
        TypedValue::Int(i) => match i.to_i64() {
            Some(small) => Value::Int(small),
            None => Value::Big(Rc::new(i.clone())),
        },
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
        TypedValue::Set(items) => {
            let mut values = Vec::with_capacity(items.borrow().len());
            for item in items.borrow().iter() {
                values.push(typed_to_value(item)?);
            }
            Value::Set(Rc::new(RefCell::new(values)))
        }
        TypedValue::Dict(entries) => {
            let mut values = Vec::with_capacity(entries.borrow().len());
            for (key, value) in entries.borrow().iter() {
                values.push((typed_to_value(key)?, typed_to_value(value)?));
            }
            Value::Dict(Rc::new(RefCell::new(values)))
        }
        TypedValue::Adt(value) => {
            let mut payload = Vec::with_capacity(value.payload.len());
            for item in value.payload.iter() {
                payload.push(typed_to_value(item)?);
            }
            Value::Adt(Rc::clone(&value.variant_name), payload)
        }
        _ => return Err("typed main returned an iterable or function value".into()),
    })
}

pub(crate) fn typed_equal(lhs: &TypedValue, rhs: &TypedValue) -> TResult<bool> {
    Ok(match (lhs, rhs) {
        (TypedValue::Unit, TypedValue::Unit) => true,
        (TypedValue::Cell(a), TypedValue::Cell(b)) => typed_equal(&a.borrow(), &b.borrow())?,
        (TypedValue::Function(_), _) | (TypedValue::Closure(_), _) => {
            return Err("functions cannot be compared".into())
        }
        (TypedValue::Bool(a), TypedValue::Bool(b)) => a == b,
        (TypedValue::Int(a), TypedValue::Int(b)) => a == b,
        (TypedValue::Float(a), TypedValue::Float(b)) => a == b,
        (TypedValue::Int(a), TypedValue::Float(b)) => cmp_int_f64(a, *b) == Some(Ordering::Equal),
        (TypedValue::Float(a), TypedValue::Int(b)) => cmp_int_f64(b, *a) == Some(Ordering::Equal),
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
        (TypedValue::Set(a), TypedValue::Set(b)) => {
            let left = a.borrow();
            let right = b.borrow();
            left.len() == right.len()
                && left.iter().all(|item| {
                    right
                        .iter()
                        .any(|other| typed_equal(item, other).unwrap_or(false))
                })
        }
        (TypedValue::Adt(a), TypedValue::Adt(b)) => {
            a.type_ == b.type_
                && a.variant == b.variant
                && a.payload.len() == b.payload.len()
                && a.payload
                    .iter()
                    .zip(b.payload.iter())
                    .all(|(l, r)| typed_equal(l, r).unwrap_or(false))
        }
        (TypedValue::Dict(a), TypedValue::Dict(b)) => {
            let left = a.borrow();
            let right = b.borrow();
            if left.len() != right.len() {
                return Ok(false);
            }
            for (key, value) in left.iter() {
                let Some(other) = dict_get(&right, key)? else {
                    return Ok(false);
                };
                if !typed_equal(value, &other)? {
                    return Ok(false);
                }
            }
            true
        }
        _ => false,
    })
}

pub(crate) fn constant_value(constant: &Constant) -> TResult<TypedValue> {
    Ok(match constant {
        Constant::Null => TypedValue::Unit,
        Constant::Bool(b) => TypedValue::Bool(*b),
        Constant::Int(i) => TypedValue::Int(BigInt::from(*i)),
        Constant::BigInt(b) => TypedValue::Int((**b).clone()),
        Constant::Float(f) => TypedValue::Float(*f),
        Constant::Str(s) => TypedValue::Str(Rc::clone(s)),
        _ => return Err("unsupported constant kind for typed LOAD_K".into()),
    })
}

pub(crate) fn typed_contains(container: &TypedValue, value: &TypedValue) -> TResult<bool> {
    match container {
        TypedValue::List(items) => {
            for item in items.borrow().iter() {
                if typed_equal(item, value)? {
                    return Ok(true);
                }
            }
            Ok(false)
        }
        TypedValue::Tuple(items) => {
            for item in items.iter() {
                if typed_equal(item, value)? {
                    return Ok(true);
                }
            }
            Ok(false)
        }
        TypedValue::Set(items) => {
            for item in items.borrow().iter() {
                if typed_equal(item, value)? {
                    return Ok(true);
                }
            }
            Ok(false)
        }
        TypedValue::Dict(entries) => {
            for (key, _) in entries.borrow().iter() {
                if typed_equal(key, value)? {
                    return Ok(true);
                }
            }
            Ok(false)
        }
        TypedValue::Str(haystack) => match value {
            TypedValue::Str(needle) => Ok(haystack.contains(&**needle)),
            _ => Err("typed String membership expects a String".into()),
        },
        _ => Err("typed membership expects a container".into()),
    }
}

fn slice_bounds(
    len: usize,
    start: Option<&TypedValue>,
    stop: Option<&TypedValue>,
) -> TResult<(usize, usize)> {
    let n = len as i64;
    let normalize = |value: i64| {
        let value = if value < 0 { value + n } else { value };
        value.clamp(0, n) as usize
    };
    let begin = match start {
        Some(value) => normalize(as_index(value)?),
        None => 0,
    };
    let end = match stop {
        Some(value) => normalize(as_index(value)?),
        None => len,
    };
    Ok((begin, end.max(begin)))
}

pub(crate) fn typed_slice(
    container: &TypedValue,
    start: Option<&TypedValue>,
    stop: Option<&TypedValue>,
) -> TResult<TypedValue> {
    match container {
        TypedValue::List(items) => {
            let items = items.borrow();
            let (begin, end) = slice_bounds(items.len(), start, stop)?;
            Ok(TypedValue::List(Rc::new(RefCell::new(
                items[begin..end].to_vec(),
            ))))
        }
        TypedValue::Tuple(items) => {
            let (begin, end) = slice_bounds(items.len(), start, stop)?;
            Ok(TypedValue::Tuple(items[begin..end].into()))
        }
        TypedValue::Str(text) => {
            let chars: Vec<char> = text.chars().collect();
            let (begin, end) = slice_bounds(chars.len(), start, stop)?;
            let slice: String = chars[begin..end].iter().collect();
            Ok(TypedValue::Str(Rc::from(slice.as_str())))
        }
        _ => Err("typed slice expects List, Tuple or String".into()),
    }
}

pub(crate) fn typed_set_op(op: u32, left: &TypedValue, right: &TypedValue) -> TResult<TypedValue> {
    let (TypedValue::Set(left), TypedValue::Set(right)) = (left, right) else {
        return Err("typed set operators expect two Sets".into());
    };
    let left = left.borrow();
    let right = right.borrow();
    let mut result: Vec<TypedValue> = Vec::new();
    let in_right = |value: &TypedValue| -> TResult<bool> {
        for item in right.iter() {
            if typed_equal(item, value)? {
                return Ok(true);
            }
        }
        Ok(false)
    };
    let mut push = |value: &TypedValue| -> TResult<()> {
        for item in result.iter() {
            if typed_equal(item, value)? {
                return Ok(());
            }
        }
        result.push(value.clone());
        Ok(())
    };
    match op {
        SET_UNION => {
            for item in left.iter() {
                push(item)?;
            }
            for item in right.iter() {
                push(item)?;
            }
        }
        SET_INTERSECT => {
            for item in left.iter() {
                if in_right(item)? {
                    push(item)?;
                }
            }
        }
        SET_DIFFERENCE => {
            for item in left.iter() {
                if !in_right(item)? {
                    push(item)?;
                }
            }
        }
        _ => {
            for item in left.iter() {
                if !in_right(item)? {
                    push(item)?;
                }
            }
            for item in right.iter() {
                let mut in_left = false;
                for existing in left.iter() {
                    if typed_equal(existing, item)? {
                        in_left = true;
                        break;
                    }
                }
                if !in_left {
                    result.push(item.clone());
                }
            }
        }
    }
    Ok(TypedValue::Set(Rc::new(RefCell::new(result))))
}

/// Set subset/superset comparisons (OP 0031 C7).
///
/// Sets are deduplicated by construction, so a proper relation is the
/// non-strict one plus a strict length comparison.
pub(crate) fn typed_set_relation(op: u32, left: &TypedValue, right: &TypedValue) -> TResult<bool> {
    let (TypedValue::Set(left), TypedValue::Set(right)) = (left, right) else {
        return Err("typed set comparisons expect two Sets".into());
    };
    let left = left.borrow();
    let right = right.borrow();
    let contains = |items: &[TypedValue], value: &TypedValue| -> TResult<bool> {
        for item in items {
            if typed_equal(item, value)? {
                return Ok(true);
            }
        }
        Ok(false)
    };
    let subset = match op {
        SET_SUBSET | SET_PROPER_SUBSET => {
            for item in left.iter() {
                if !contains(&right, item)? {
                    return Ok(false);
                }
            }
            true
        }
        _ => {
            for item in right.iter() {
                if !contains(&left, item)? {
                    return Ok(false);
                }
            }
            true
        }
    };
    if !subset {
        return Ok(false);
    }
    Ok(match op {
        SET_PROPER_SUBSET => left.len() < right.len(),
        SET_PROPER_SUPERSET => right.len() < left.len(),
        _ => true,
    })
}

/// Ordering of two scalar elements. Lists are homogeneous by typing, but mixed
/// numerics are still compared exactly; an unordered pair (NaN) is an error,
/// matching the dynamic dialect's lexicographic comparison.
fn scalar_order(left: &TypedValue, right: &TypedValue) -> TResult<Ordering> {
    match (left, right) {
        (TypedValue::Int(a), TypedValue::Int(b)) => Ok(a.cmp(b)),
        (TypedValue::Float(a), TypedValue::Float(b)) => a
            .partial_cmp(b)
            .ok_or_else(|| "List elements are not orderable".to_string()),
        (TypedValue::Str(a), TypedValue::Str(b)) => Ok(a.cmp(b)),
        (TypedValue::Int(_), TypedValue::Float(_)) | (TypedValue::Float(_), TypedValue::Int(_)) => {
            mixed_cmp(left, right)?.ok_or_else(|| "List elements are not orderable".to_string())
        }
        _ => Err("List elements are not orderable".into()),
    }
}

/// Lexicographic comparison of two lists: -1, 0 or 1.
pub(crate) fn typed_list_cmp(left: &TypedValue, right: &TypedValue) -> TResult<i32> {
    let (TypedValue::List(left), TypedValue::List(right)) = (left, right) else {
        return Err("typed List comparison requires two Lists".into());
    };
    let left = left.borrow();
    let right = right.borrow();
    for (a, b) in left.iter().zip(right.iter()) {
        if typed_equal(a, b)? {
            continue;
        }
        return Ok(match scalar_order(a, b)? {
            Ordering::Less => -1,
            Ordering::Greater => 1,
            Ordering::Equal => continue,
        });
    }
    Ok(match left.len().cmp(&right.len()) {
        Ordering::Less => -1,
        Ordering::Greater => 1,
        Ordering::Equal => 0,
    })
}

pub(crate) fn typed_list_concat(left: &TypedValue, right: &TypedValue) -> TResult<TypedValue> {
    let (TypedValue::List(left), TypedValue::List(right)) = (left, right) else {
        return Err("typed List '+' requires two Lists".into());
    };
    let mut values = left.borrow().clone();
    values.extend(right.borrow().iter().cloned());
    Ok(TypedValue::List(Rc::new(RefCell::new(values))))
}

/// Stabilize scalar sorting like Python: NaN compares equal to everything, so
/// it keeps its position relative to neighbors. Element types are validated
/// before sorting, which keeps the comparator infallible.
fn sort_order(left: &TypedValue, right: &TypedValue) -> Ordering {
    match (left, right) {
        (TypedValue::Int(a), TypedValue::Int(b)) => a.cmp(b),
        (TypedValue::Float(a), TypedValue::Float(b)) => a.partial_cmp(b).unwrap_or(Ordering::Equal),
        (TypedValue::Str(a), TypedValue::Str(b)) => a.cmp(b),
        (TypedValue::Int(_), TypedValue::Float(_)) | (TypedValue::Float(_), TypedValue::Int(_)) => {
            mixed_cmp(left, right)
                .ok()
                .flatten()
                .unwrap_or(Ordering::Equal)
        }
        _ => Ordering::Equal,
    }
}

pub(crate) fn sort_typed_values(values: &mut [TypedValue]) -> TResult<()> {
    for value in values.iter() {
        if !matches!(
            value,
            TypedValue::Int(_) | TypedValue::Float(_) | TypedValue::Str(_)
        ) {
            return Err("sorted expects a List of Int, Float or String".into());
        }
    }
    values.sort_by(sort_order);
    Ok(())
}

/// Resolve one `LOAD_OUTER`/`STORE_OUTER` target.
///
/// `depth` is 1-based from the executing closure: depth 1 is its own snapshot,
/// depth 2 the creator's, and so on (so we hop `depth - 1` parents). Slot
/// numbers index that snapshot's registers.
pub(crate) fn closure_slot<'a>(
    closure: Option<&'a Rc<TypedClosure>>,
    depth: usize,
    slot: usize,
) -> TResult<&'a TypedValue> {
    if depth < 1 {
        return Err("invalid closure depth in typed bytecode".into());
    }
    let mut current = closure.ok_or("invalid closure depth in typed bytecode")?;
    for _ in 0..(depth - 1) {
        current = current
            .parent
            .as_ref()
            .ok_or("invalid closure depth in typed bytecode")?;
    }
    current
        .snapshot
        .get(slot)
        .ok_or_else(|| "invalid closure slot in typed bytecode".to_string())
}

pub(crate) fn unwrap_cell(value: &TypedValue) -> std::borrow::Cow<'_, TypedValue> {
    match value {
        TypedValue::Cell(cell) => std::borrow::Cow::Owned(cell.borrow().clone()),
        other => std::borrow::Cow::Borrowed(other),
    }
}

pub(crate) fn as_int(value: &TypedValue) -> TResult<&BigInt> {
    match value {
        TypedValue::Int(i) => Ok(i),
        _ => Err("typed opcode expected Int".into()),
    }
}

pub(crate) fn as_index(value: &TypedValue) -> TResult<i64> {
    as_int(value)?
        .to_i64()
        .ok_or_else(|| "integer index is too large".to_string())
}

pub(crate) fn as_float(value: &TypedValue) -> TResult<f64> {
    match value {
        TypedValue::Float(f) => Ok(*f),
        _ => Err("typed opcode expected Float".into()),
    }
}

pub(crate) fn as_bool(value: &TypedValue) -> TResult<bool> {
    match value {
        TypedValue::Bool(b) => Ok(*b),
        _ => Err("typed opcode expected Bool".into()),
    }
}

pub(crate) fn as_str(value: &TypedValue) -> TResult<&str> {
    match value {
        TypedValue::Str(s) => Ok(s.as_ref()),
        _ => Err("typed opcode expected String".into()),
    }
}

pub(crate) fn guard(expected: &TypedType, value: &TypedValue) -> TResult<()> {
    if let (TypedType::Adt(_, _), TypedValue::Adt(adt)) = (expected, value) {
        return if adt.type_ == *expected {
            Ok(())
        } else {
            Err(format!(
                "typed bytecode guard failed: expected {expected:?}"
            ))
        };
    }
    let ok = matches!(
        (expected, value),
        (TypedType::Int, TypedValue::Int(_))
            | (TypedType::Float, TypedValue::Float(_))
            | (TypedType::Bool, TypedValue::Bool(_))
            | (TypedType::String, TypedValue::Str(_))
            | (TypedType::Unit, TypedValue::Unit)
            | (TypedType::List(_), TypedValue::List(_))
            | (TypedType::Tuple(_), TypedValue::Tuple(_))
            | (TypedType::Set(_), TypedValue::Set(_))
            | (TypedType::Dict(_, _), TypedValue::Dict(_))
            | (TypedType::Adt(_, _), TypedValue::Adt(_))
            | (TypedType::Iterator, TypedValue::Iterator(_))
            | (
                TypedType::Function,
                TypedValue::Function(_) | TypedValue::Native(_)
            )
    );
    if ok {
        Ok(())
    } else {
        Err(format!(
            "typed bytecode guard failed: expected {expected:?}"
        ))
    }
}

pub(crate) fn open_iterator(value: &TypedValue) -> TResult<TypedValue> {
    let values = match value {
        TypedValue::List(items) => items.borrow().clone(),
        TypedValue::Tuple(items) => items.to_vec(),
        TypedValue::Set(items) => items.borrow().clone(),
        TypedValue::Dict(entries) => entries
            .borrow()
            .iter()
            .map(|(key, _)| key.clone())
            .collect(),
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

pub(crate) fn iterator_next(value: &TypedValue) -> TResult<(TypedValue, bool)> {
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

pub(crate) fn set_insert(items: &mut Vec<TypedValue>, value: TypedValue) -> TResult<()> {
    for item in items.iter() {
        if typed_equal(item, &value)? {
            return Ok(());
        }
    }
    items.push(value);
    Ok(())
}

pub(crate) fn dict_set(
    entries: &mut Vec<(TypedValue, TypedValue)>,
    key: TypedValue,
    value: TypedValue,
) -> TResult<()> {
    for (existing_key, existing_value) in entries.iter_mut() {
        if typed_equal(existing_key, &key)? {
            *existing_value = value;
            return Ok(());
        }
    }
    entries.push((key, value));
    Ok(())
}

pub(crate) fn dict_get(
    entries: &[(TypedValue, TypedValue)],
    key: &TypedValue,
) -> TResult<Option<TypedValue>> {
    for (existing_key, value) in entries.iter() {
        if typed_equal(existing_key, key)? {
            return Ok(Some(value.clone()));
        }
    }
    Ok(None)
}

pub(crate) fn adt_constructor(
    adt_decls: &[TypedAdtDecl],
    constructor_id: u16,
) -> TResult<(u16, u16, &(String, u8))> {
    let mut current = 0u16;
    for (decl_index, decl) in adt_decls.iter().enumerate() {
        for (ctor_index, constructor) in decl.constructors.iter().enumerate() {
            if current == constructor_id {
                return Ok((decl_index as u16, ctor_index as u16, constructor));
            }
            current += 1;
        }
    }
    Err("typed ADT constructor id out of range".into())
}

pub(crate) fn get_item(container: &TypedValue, index: &TypedValue) -> TResult<TypedValue> {
    if let TypedValue::Dict(entries) = container {
        return match dict_get(&entries.borrow(), index)? {
            Some(value) => Ok(value),
            None => Err("key not found".into()),
        };
    }
    let index = as_index(index)?;
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

pub(crate) fn normalize_index(index: i64, len: usize) -> TResult<usize> {
    let len_i64 = len as i64;
    let normalized = if index < 0 { index + len_i64 } else { index };
    if normalized < 0 || normalized >= len_i64 {
        return Err("index out of range".into());
    }
    Ok(normalized as usize)
}

pub(crate) fn mixed_cmp(lhs: &TypedValue, rhs: &TypedValue) -> TResult<Option<Ordering>> {
    match (lhs, rhs) {
        (TypedValue::Int(a), TypedValue::Int(b)) => Ok(Some(a.cmp(b))),
        (TypedValue::Float(a), TypedValue::Float(b)) => Ok(a.partial_cmp(b)),
        (TypedValue::Int(a), TypedValue::Float(b)) => Ok(cmp_int_f64(a, *b)),
        (TypedValue::Float(a), TypedValue::Int(b)) => {
            Ok(cmp_int_f64(b, *a).map(|ordering| ordering.reverse()))
        }
        _ => Err("typed mixed comparison expects Int or Float".into()),
    }
}

/// Exact comparison between i64 and f64 (no rounding of the integer).
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

// Typed opcodes (bytecode/typed_opcodes.py).
#[cfg(test)]
mod tests {
    use super::*;

    fn int(value: i64) -> TypedValue {
        TypedValue::Int(BigInt::from(value))
    }

    #[test]
    fn mixed_comparison_is_exact_at_2_pow_53() {
        // 2^53 + 1 cannot be represented as f64; the comparison must not round.
        let big = int(9_007_199_254_740_993);
        let as_float = TypedValue::Float(9_007_199_254_740_992.0);
        assert_eq!(mixed_cmp(&big, &as_float).unwrap(), Some(Ordering::Greater));
        assert_eq!(mixed_cmp(&as_float, &big).unwrap(), Some(Ordering::Less));
        assert_eq!(
            mixed_cmp(&int(9_007_199_254_740_992), &as_float).unwrap(),
            Some(Ordering::Equal)
        );
    }

    #[test]
    fn mixed_comparison_handles_nan_and_infinity() {
        let nan = TypedValue::Float(f64::NAN);
        assert_eq!(mixed_cmp(&nan, &int(1)).unwrap(), None);
        assert_eq!(mixed_cmp(&int(1), &nan).unwrap(), None);
        assert_eq!(
            mixed_cmp(&TypedValue::Float(f64::INFINITY), &int(i64::MAX)).unwrap(),
            Some(Ordering::Greater)
        );
    }

    #[test]
    fn guard_rejects_wrong_types() {
        assert!(guard(&TypedType::Int, &int(1)).is_ok());
        assert!(guard(&TypedType::Int, &TypedValue::Bool(true)).is_err());
        assert!(guard(&TypedType::Unit, &TypedValue::Unit).is_ok());
    }

    #[test]
    fn typed_values_display_like_python() {
        assert_eq!(display_typed(&TypedValue::Float(2.0)), "2.0");
        assert_eq!(display_typed(&TypedValue::Float(-0.0)), "-0.0");
        assert_eq!(display_typed(&TypedValue::Unit), "null");
    }

    fn set_value(values: &[TypedValue]) -> TypedValue {
        let mut items = Vec::new();
        for value in values {
            set_insert(&mut items, value.clone()).unwrap();
        }
        TypedValue::Set(Rc::new(RefCell::new(items)))
    }

    fn dict_value(entries: &[(TypedValue, TypedValue)]) -> TypedValue {
        let mut items = Vec::new();
        for (key, value) in entries {
            dict_set(&mut items, key.clone(), value.clone()).unwrap();
        }
        TypedValue::Dict(Rc::new(RefCell::new(items)))
    }

    #[test]
    fn set_deduplicates_with_typed_equality() {
        let value = set_value(&[int(1), int(2), int(1)]);
        let TypedValue::Set(items) = &value else {
            panic!("expected a set");
        };
        assert_eq!(items.borrow().len(), 2);
        assert_eq!(display_typed(&value), "{. 1, 2 .}");
    }

    #[test]
    fn dict_preserves_insertion_order_and_replaces_values() {
        let value = dict_value(&[
            (TypedValue::Str(Rc::from("b")), int(2)),
            (TypedValue::Str(Rc::from("a")), int(1)),
            (TypedValue::Str(Rc::from("b")), int(3)),
        ]);
        let TypedValue::Dict(entries) = &value else {
            panic!("expected a dict");
        };
        let entries = entries.borrow();
        assert_eq!(entries.len(), 2);
        assert_eq!(display_typed(&value), "{: b: 3, a: 1 :}");
        assert!(dict_get(&entries, &TypedValue::Str(Rc::from("a")))
            .unwrap()
            .is_some());
    }

    #[test]
    fn adt_display_and_equality() {
        let make = |value: i64| {
            TypedValue::Adt(Rc::new(TypedAdt {
                type_: TypedType::Adt(0, vec![]),
                variant: 0,
                variant_name: Rc::from("Circle"),
                payload: Box::new([TypedValue::Int(BigInt::from(value))]),
            }))
        };
        assert_eq!(display_typed(&make(2)), "Circle(2)");
        assert!(typed_equal(&make(2), &make(2)).unwrap());
        assert!(!typed_equal(&make(2), &make(3)).unwrap());
    }

    #[test]
    fn set_and_dict_equality_ignore_insertion_order() {
        let left_set = set_value(&[int(1), int(2)]);
        let right_set = set_value(&[int(2), int(1)]);
        assert!(typed_equal(&left_set, &right_set).unwrap());

        let left_dict = dict_value(&[
            (TypedValue::Str(Rc::from("a")), int(1)),
            (TypedValue::Str(Rc::from("b")), int(2)),
        ]);
        let right_dict = dict_value(&[
            (TypedValue::Str(Rc::from("b")), int(2)),
            (TypedValue::Str(Rc::from("a")), int(1)),
        ]);
        assert!(typed_equal(&left_dict, &right_dict).unwrap());
    }

    fn list_value(values: Vec<TypedValue>) -> TypedValue {
        TypedValue::List(Rc::new(RefCell::new(values)))
    }

    #[test]
    fn list_compare_is_lexicographic() {
        let cases = [
            (vec![int(1), int(2)], vec![int(1), int(3)], -1),
            (vec![int(1), int(2)], vec![int(1), int(2)], 0),
            (vec![int(1)], vec![int(1), int(2)], -1),
            (vec![], vec![int(1)], -1),
            (vec![int(2)], vec![int(1), int(9)], 1),
        ];
        for (left, right, expected) in cases {
            assert_eq!(
                typed_list_cmp(&list_value(left), &list_value(right)).unwrap(),
                expected
            );
        }
        let a = list_value(vec![TypedValue::Str(Rc::from("a"))]);
        let b = list_value(vec![TypedValue::Str(Rc::from("b"))]);
        assert_eq!(typed_list_cmp(&a, &b).unwrap(), -1);
    }

    #[test]
    fn list_concat_returns_a_new_list() {
        let left = list_value(vec![int(1)]);
        let right = list_value(vec![int(2)]);
        let combined = typed_list_concat(&left, &right).unwrap();
        assert_eq!(display_typed(&combined), "[1, 2]");
        assert_eq!(display_typed(&left), "[1]");
        assert_eq!(display_typed(&right), "[2]");
    }

    #[test]
    fn sort_typed_values_orders_scalars() {
        let mut values = vec![int(3), int(1), int(2)];
        sort_typed_values(&mut values).unwrap();
        let shown: Vec<String> = values.iter().map(display_typed).collect();
        assert_eq!(shown, ["1", "2", "3"]);

        let mut words = vec![
            TypedValue::Str(Rc::from("b")),
            TypedValue::Str(Rc::from("a")),
        ];
        sort_typed_values(&mut words).unwrap();
        let shown: Vec<String> = words.iter().map(display_typed).collect();
        assert_eq!(shown, ["a", "b"]);
    }
}
