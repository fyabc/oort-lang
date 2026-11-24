//! Typed bytecode (`obc` kind=1) reader and register VM (design 15 M4 U1).
//!
//! Scalar registers use `TypedValue` instead of boxed `vm::Value`: Int is an
//! arbitrary-precision BigInt, Float is f64, Bool is bool, Unit carries no
//! payload. Heap values (strings, containers, closures, cells) stay behind
//! `Rc`/`RefCell`. Conversions happen only at the native `print` boundary and
//! when reporting the main result. Semantics mirror the Python typed VM.
//!
//! Accepted file versions are exact, never inferred: kind=1 typed proto v10,
//! kind=1 module artifact v12, kind=2 linked bundle v5. Malformed bytecode
//! (unknown opcode/tag/version, out-of-range index) is rejected explicitly;
//! numeric semantics follow docs/design/16-numeric-semantics.md.
//!
//! Layout:
//! - proto / bundle / artifact decoding;
//! - module artifact linker (import checks, ADT merge, id relocation);
//! - runtime values and opcode helpers;
//! - `execute` and the opcode dispatch loop.

use std::cell::{Cell, RefCell};
use std::cmp::Ordering;
use std::collections::HashMap;
use std::rc::Rc;

use num_bigint::BigInt;
use num_integer::Integer;
use num_rational::BigRational;
use num_traits::{ToPrimitive, Zero};

use crate::obc::{Constant, Reader};
use crate::vm::{float_repr, Value};

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
    Adt(u16, Vec<TypedType>),
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
    /// Registers wrapped into `Cell`s at frame entry: locals and parameters
    /// that any lambda subtree reads or writes. The compiler resolves them
    /// statically along the creator chain; readers reject slots >= register_count.
    pub cells: Vec<u16>,
    pub code: Vec<u32>,
    pub constants: Vec<Constant>,
}

#[derive(Debug, Clone)]
pub struct TypedAdtDecl {
    pub origin: String,
    pub name: String,
    pub constructors: Vec<(String, u8)>,
}

impl TypedAdtDecl {
    fn constructor(&self, index: u16) -> TResult<&(String, u8)> {
        self.constructors
            .get(index as usize)
            .ok_or_else(|| "ADT constructor index out of range".to_string())
    }
}

#[derive(Debug, Clone)]
pub struct TypedModule {
    pub functions: Vec<Rc<TypedProto>>,
    pub main: Rc<TypedProto>,
    pub adt_decls: Vec<TypedAdtDecl>,
}

fn read_type_table(
    r: &mut Reader<'_>,
    name: &str,
    adt_decls: &[TypedAdtDecl],
) -> TResult<Vec<TypedType>> {
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
            12 => {
                let decl_id = r.u16()?;
                if decl_id as usize >= adt_decls.len() {
                    return Err(format!(
                        "typed proto '{name}' has an unknown ADT declaration"
                    ));
                }
                let mut arguments = Vec::new();
                for _ in 0..r.u16()? {
                    let child = r.u16()? as usize;
                    if child >= types.len() {
                        return Err(format!("typed proto '{name}' has a forward type reference"));
                    }
                    arguments.push(types[child].clone());
                }
                TypedType::Adt(decl_id, arguments)
            }
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

fn read_proto(r: &mut Reader<'_>, adt_decls: &[TypedAdtDecl]) -> TResult<TypedProto> {
    let name = r.string()?;
    let is_main = r.boolean()?;
    let types = read_type_table(r, &name, adt_decls)?;
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
    let mut cells = Vec::new();
    for _ in 0..r.u16()? {
        let slot = r.u16()?;
        if slot >= register_count {
            return Err(format!(
                "typed proto '{name}' has an out-of-range cell slot"
            ));
        }
        cells.push(slot);
    }
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
        cells,
        code,
        constants,
    })
}

/// Read a single-module typed program (kind=1, proto version 10): ADT
/// declarations, function protos, then main. Used for `-t tvm` artifacts that
/// were never split into modules.
pub fn read_typed_module(data: &[u8]) -> TResult<TypedModule> {
    if data.len() < 5 || &data[0..3] != b"OBC" {
        return Err("not an Oort bytecode file (bad magic)".into());
    }
    let kind = data[3];
    if kind != 1 {
        return Err(format!("expected typed bytecode (kind=1), got kind={kind}"));
    }
    let version = data[4];
    if version != 10 {
        return Err(format!("unsupported typed bytecode version {version}"));
    }
    let mut r = Reader::new(&data[5..]);
    let nadt = r.u32()?;
    let mut adt_decls = Vec::with_capacity(nadt as usize);
    for _ in 0..nadt {
        let origin = r.string()?;
        let name = r.string()?;
        let ctor_count = r.u16()?;
        let mut constructors = Vec::with_capacity(ctor_count as usize);
        for _ in 0..ctor_count {
            let ctor_name = r.string()?;
            let arity = r.u8()?;
            constructors.push((ctor_name, arity));
        }
        adt_decls.push(TypedAdtDecl {
            origin,
            name,
            constructors,
        });
    }
    let nf = r.u32()?;
    let mut functions = Vec::with_capacity(nf as usize);
    for _ in 0..nf {
        functions.push(Rc::new(read_proto(&mut r, &adt_decls)?));
    }
    let main = Rc::new(read_proto(&mut r, &adt_decls)?);
    Ok(TypedModule {
        functions,
        main,
        adt_decls,
    })
}

/// Read a linked typed bundle (kind=2): one merged program with a flat
/// constructor table whose order matches the declaration table.
pub fn read_linked_bundle(data: &[u8]) -> TResult<TypedModule> {
    if data.len() < 5 || &data[0..3] != b"OBC" {
        return Err("not an Oort bytecode file (bad magic)".into());
    }
    let kind = data[3];
    if kind != 2 {
        return Err(format!(
            "expected linked typed bundle (kind=2), got kind={kind}"
        ));
    }
    let version = data[4];
    if version != 5 {
        return Err(format!("unsupported linked bundle version {version}"));
    }
    let mut r = Reader::new(&data[5..]);
    let abi_version = r.u16()?;
    if abi_version != 1 {
        return Err(format!(
            "unsupported linked bundle ABI version {abi_version}"
        ));
    }

    let nadt = r.u32()?;
    let mut adt_decls = Vec::with_capacity(nadt as usize);
    for _ in 0..nadt {
        let origin = r.string()?;
        let name = r.string()?;
        let ctor_count = r.u16()?;
        let mut constructors = Vec::with_capacity(ctor_count as usize);
        for _ in 0..ctor_count {
            let ctor_name = r.string()?;
            let arity = r.u8()?;
            constructors.push((ctor_name, arity));
        }
        adt_decls.push(TypedAdtDecl {
            origin,
            name,
            constructors,
        });
    }

    let nctor = r.u32()?;
    let mut table = Vec::with_capacity(nctor as usize);
    for _ in 0..nctor {
        table.push((r.string()?, r.string()?, r.string()?, r.u16()?));
    }
    let mut expected = Vec::new();
    for decl in &adt_decls {
        for (name, arity) in &decl.constructors {
            expected.push((
                decl.origin.clone(),
                decl.name.clone(),
                name.clone(),
                *arity as u16,
            ));
        }
    }
    if table != expected {
        return Err("linked bundle constructor table does not match its declarations".into());
    }

    let nf = r.u32()?;
    let mut functions = Vec::with_capacity(nf as usize);
    for _ in 0..nf {
        functions.push(Rc::new(read_proto(&mut r, &adt_decls)?));
    }
    let main = Rc::new(read_proto(&mut r, &adt_decls)?);
    Ok(TypedModule {
        functions,
        main,
        adt_decls,
    })
}

// ----------------------------------------------------------------------
// v12 module artifacts and the native linker (P1c-3)
// ----------------------------------------------------------------------

#[derive(Debug, Clone)]
pub struct TypedExport {
    pub kind: u8,
    pub name: String,
    pub adt_name: String,
    pub symbol: u32,
    pub abi_hash: i64,
}

#[derive(Debug, Clone)]
pub struct TypedImport {
    pub module_id: String,
    pub kind: u8,
    pub name: String,
    pub expected_abi_hash: i64,
}

#[derive(Debug, Clone)]
pub struct TypedConstructorRef {
    pub origin: String,
    pub adt_name: String,
    pub name: String,
    pub arity: u16,
}

/// One module compiled to its own artifact (kind=1, version 12).
///
/// Export/import tables describe module edges; `module.adt_decls` and
/// `constructors` still use artifact-local ids that the linker remaps.
#[derive(Debug, Clone)]
pub struct TypedArtifact {
    pub module_id: String,
    pub abi_version: u16,
    pub exports: Vec<TypedExport>,
    pub imports: Vec<TypedImport>,
    pub constructors: Vec<TypedConstructorRef>,
    pub module: TypedModule,
}

/// Read a kind=1 module artifact (v12). Version 10 is the standalone
/// single-module format and is not accepted here.
pub fn read_typed_artifact(data: &[u8]) -> TResult<TypedArtifact> {
    if data.len() < 5 || &data[0..3] != b"OBC" {
        return Err("not an Oort bytecode file (bad magic)".into());
    }
    let kind = data[3];
    if kind != 1 {
        return Err(format!(
            "expected typed module artifact (kind=1), got kind={kind}"
        ));
    }
    let version = data[4];
    if version != 12 {
        return Err(format!(
            "unsupported typed module artifact version {version}"
        ));
    }
    let mut r = Reader::new(&data[5..]);
    let module_id = r.string()?;
    let abi_version = r.u16()?;
    if abi_version != 1 {
        return Err(format!(
            "unsupported typed module ABI version {abi_version}"
        ));
    }

    let nexports = r.u32()?;
    let mut exports = Vec::with_capacity(nexports as usize);
    for _ in 0..nexports {
        exports.push(TypedExport {
            kind: r.u8()?,
            name: r.string()?,
            adt_name: r.string()?,
            symbol: r.u32()?,
            abi_hash: r.i64()?,
        });
    }

    let nimports = r.u32()?;
    let mut imports = Vec::with_capacity(nimports as usize);
    for _ in 0..nimports {
        imports.push(TypedImport {
            module_id: r.string()?,
            kind: r.u8()?,
            name: r.string()?,
            expected_abi_hash: r.i64()?,
        });
    }

    let nconstructors = r.u32()?;
    let mut constructors = Vec::with_capacity(nconstructors as usize);
    for _ in 0..nconstructors {
        constructors.push(TypedConstructorRef {
            origin: r.string()?,
            adt_name: r.string()?,
            name: r.string()?,
            arity: r.u16()?,
        });
    }

    let nadt = r.u32()?;
    let mut adt_decls = Vec::with_capacity(nadt as usize);
    for _ in 0..nadt {
        let origin = r.string()?;
        let name = r.string()?;
        let ctor_count = r.u16()?;
        let mut decl_constructors = Vec::with_capacity(ctor_count as usize);
        for _ in 0..ctor_count {
            let ctor_name = r.string()?;
            let arity = r.u8()?;
            decl_constructors.push((ctor_name, arity));
        }
        adt_decls.push(TypedAdtDecl {
            origin,
            name,
            constructors: decl_constructors,
        });
    }

    let nf = r.u32()?;
    let mut functions = Vec::with_capacity(nf as usize);
    for _ in 0..nf {
        functions.push(Rc::new(read_proto(&mut r, &adt_decls)?));
    }
    let main = Rc::new(read_proto(&mut r, &adt_decls)?);
    if !r.is_eof() {
        return Err("trailing bytes in typed module artifact".into());
    }
    Ok(TypedArtifact {
        module_id,
        abi_version,
        exports,
        imports,
        constructors,
        module: TypedModule {
            functions,
            main,
            adt_decls,
        },
    })
}

fn fnv1a(text: &str) -> i64 {
    let mut value: u64 = 0xCBF29CE484222325;
    for byte in text.as_bytes() {
        value ^= *byte as u64;
        value = (value.wrapping_mul(0x100000001B3)) & 0x7FFF_FFFF_FFFF_FFFF;
    }
    value as i64
}

fn export_kind_name(kind: u8) -> &'static str {
    match kind {
        1 => "function",
        2 => "adt",
        3 => "constructor",
        _ => "?",
    }
}

fn module_abi_hash(artifact: &TypedArtifact) -> i64 {
    let mut entries: Vec<(String, String, i64)> = artifact
        .exports
        .iter()
        .map(|export| {
            (
                export_kind_name(export.kind).to_string(),
                export.name.clone(),
                export.abi_hash,
            )
        })
        .collect();
    entries.sort();
    let text = entries
        .iter()
        .map(|(kind, name, hash)| format!("{kind}:{name}:{hash}"))
        .collect::<Vec<_>>()
        .join("\n");
    fnv1a(&text)
}

fn find_export<'a>(artifact: &'a TypedArtifact, kind: u8, name: &str) -> Option<&'a TypedExport> {
    artifact
        .exports
        .iter()
        .find(|export| export.kind == kind && export.name == name)
}

fn remap_type(ty: &TypedType, decl_map: &HashMap<u16, u16>) -> TResult<TypedType> {
    Ok(match ty {
        TypedType::Adt(decl_id, args) => {
            let mapped = *decl_map
                .get(decl_id)
                .ok_or_else(|| "ADT declaration id out of range".to_string())?;
            let mut mapped_args = Vec::with_capacity(args.len());
            for argument in args {
                mapped_args.push(remap_type(argument, decl_map)?);
            }
            TypedType::Adt(mapped, mapped_args)
        }
        TypedType::List(element) => TypedType::List(Box::new(remap_type(element, decl_map)?)),
        TypedType::Set(element) => TypedType::Set(Box::new(remap_type(element, decl_map)?)),
        TypedType::Dict(key, value) => TypedType::Dict(
            Box::new(remap_type(key, decl_map)?),
            Box::new(remap_type(value, decl_map)?),
        ),
        TypedType::Tuple(elements) => {
            let mut mapped = Vec::with_capacity(elements.len());
            for element in elements {
                mapped.push(remap_type(element, decl_map)?);
            }
            TypedType::Tuple(mapped)
        }
        other => other.clone(),
    })
}

fn remap_proto(
    proto: &Rc<TypedProto>,
    decl_map: &HashMap<u16, u16>,
    ctor_map: &HashMap<u8, u16>,
    function_map: Option<&HashMap<u16, u16>>,
) -> TResult<Rc<TypedProto>> {
    let mut copy = (**proto).clone();
    let mut types = Vec::with_capacity(copy.types.len());
    for ty in &copy.types {
        types.push(remap_type(ty, decl_map)?);
    }
    copy.types = types;
    let mut param_types = Vec::with_capacity(copy.param_types.len());
    for ty in &copy.param_types {
        param_types.push(remap_type(ty, decl_map)?);
    }
    copy.param_types = param_types;
    copy.ret_type = remap_type(&copy.ret_type, decl_map)?;
    for word in &mut copy.code {
        let op = *word >> 24;
        if op == NEW_ADT {
            let a = (*word >> 16) & 0xff;
            let b = ((*word >> 8) & 0xff) as u8;
            let c = *word & 0xff;
            let mapped = *ctor_map
                .get(&b)
                .ok_or_else(|| "typed constructor symbol out of range".to_string())?;
            *word = (op << 24) | (a << 16) | ((mapped as u32) << 8) | c;
        } else if op == DEF_FUN || op == MK_FUN || op == MK_CLOSURE {
            if let Some(function_map) = function_map {
                let a = (*word >> 16) & 0xff;
                let bx = (*word & 0xffff) as u16;
                let mapped = *function_map
                    .get(&bx)
                    .ok_or_else(|| "typed function index out of range".to_string())?;
                *word = (op << 24) | (a << 16) | mapped as u32;
            }
        }
    }
    Ok(Rc::new(copy))
}

/// Depth-first walk over the import graph. `state` is 0 = unvisited,
/// 1 = on the stack (cycle if reached again), 2 = finished. Each import is
/// resolved to its export and its pinned ABI hash (0 = unpinned) is checked.
/// `order` receives dependencies before the modules that import them.
fn visit_artifact(
    module_id: &str,
    modules: &HashMap<String, TypedArtifact>,
    state: &mut HashMap<String, u8>,
    order: &mut Vec<String>,
) -> TResult<()> {
    match state.get(module_id).copied().unwrap_or(0) {
        1 => {
            return Err(format!(
                "circular typed module import involving '{module_id}'"
            ))
        }
        2 => return Ok(()),
        _ => {}
    }
    state.insert(module_id.to_string(), 1);
    let artifact = modules
        .get(module_id)
        .ok_or_else(|| format!("missing typed module '{module_id}'"))?;
    for import in &artifact.imports {
        let dependency = modules.get(&import.module_id).ok_or_else(|| {
            format!(
                "typed module '{}' imports missing module '{}'",
                artifact.module_id, import.module_id
            )
        })?;
        let export_kind = match import.kind {
            1 => None,
            2 => Some(1),
            3 => Some(2),
            4 => Some(3),
            _ => return Err(format!("invalid typed import kind {}", import.kind)),
        };
        let actual = match export_kind {
            None => module_abi_hash(dependency),
            Some(kind) => {
                let export = find_export(dependency, kind, &import.name).ok_or_else(|| {
                    format!(
                        "typed module '{}' does not export kind {} '{}'",
                        dependency.module_id, import.kind, import.name
                    )
                })?;
                export.abi_hash
            }
        };
        if import.expected_abi_hash != 0 && import.expected_abi_hash != actual {
            return Err(format!(
                "typed ABI hash mismatch for '{}::{}'",
                dependency.module_id, import.name
            ));
        }
        visit_artifact(&import.module_id, modules, state, order)?;
    }
    state.insert(module_id.to_string(), 2);
    order.push(module_id.to_string());
    Ok(())
}

/// Link v12 module artifacts into one typed module for the Rust VM.
///
/// Phases:
/// 1. index artifacts by `module_id` and DFS the import graph (cycles and
///    missing modules are rejected; pinned ABI hashes are verified);
/// 2. merge ADT declarations by `(origin, name)` — identical duplicates from
///    different modules collapse, conflicting bodies are rejected — and give
///    each declaration a base offset in the flat constructor table;
/// 3. per module, map local ADT ids and constructor symbols to linked ids;
/// 4. assign every function a global slot (root module first) and rewrite all
///    protos; lambda names are exempt from the export-name collision check;
/// 5. rewrite the root's main once every function slot exists.
pub fn link_artifacts(
    root: TypedArtifact,
    dependencies: Vec<TypedArtifact>,
) -> TResult<TypedModule> {
    let root_id = root.module_id.clone();
    let mut modules: HashMap<String, TypedArtifact> = HashMap::new();
    for artifact in dependencies {
        if modules
            .insert(artifact.module_id.clone(), artifact)
            .is_some()
        {
            return Err("duplicate typed module id".into());
        }
    }
    if modules.insert(root.module_id.clone(), root).is_some() {
        return Err("duplicate typed module id".into());
    }

    let mut order: Vec<String> = Vec::new();
    let mut state: HashMap<String, u8> = HashMap::new();
    visit_artifact(&root_id, &modules, &mut state, &mut order)?;

    // Phase 2: merge ADT declarations. Ids are nominal by (origin, name);
    // constructor ids are flat positions across declarations, so each
    // declaration records where its constructor run starts.
    let mut merged: Vec<TypedAdtDecl> = Vec::new();
    let mut decl_index: HashMap<(String, String), u16> = HashMap::new();
    let mut bases: HashMap<(String, String), u16> = HashMap::new();
    let mut constructor_total: u16 = 0;
    for module_id in &order {
        for decl in &modules[module_id].module.adt_decls {
            let key = (decl.origin.clone(), decl.name.clone());
            if let Some(existing) = decl_index.get(&key) {
                let known = &merged[*existing as usize];
                if known.constructors != decl.constructors {
                    return Err(format!(
                        "typed ADT '{}' from '{}' has conflicting definitions",
                        decl.name, decl.origin
                    ));
                }
                continue;
            }
            let index = u16::try_from(merged.len())
                .map_err(|_| "too many typed ADT declarations".to_string())?;
            decl_index.insert(key.clone(), index);
            bases.insert(key, constructor_total);
            constructor_total = constructor_total
                .checked_add(decl.constructors.len() as u16)
                .ok_or_else(|| "too many typed constructors".to_string())?;
            merged.push(decl.clone());
        }
    }
    if constructor_total > 255 {
        return Err("linked constructor table exceeds 255 entries".into());
    }

    // Phase 3: per-module relocation maps. `NEW_ADT` operands index the
    // artifact's constructor symbol table, so symbols are resolved to
    // (declaration, position) and then to a flat global id.
    let mut maps: HashMap<String, (HashMap<u16, u16>, HashMap<u8, u16>)> = HashMap::new();
    for module_id in &order {
        let artifact = &modules[module_id];
        let mut decl_map = HashMap::new();
        for (local, decl) in artifact.module.adt_decls.iter().enumerate() {
            let key = (decl.origin.clone(), decl.name.clone());
            let mapped = *decl_index
                .get(&key)
                .ok_or_else(|| "ADT declaration missing from merged table".to_string())?;
            decl_map.insert(
                u16::try_from(local).map_err(|_| "too many ADT declarations".to_string())?,
                mapped,
            );
        }
        let mut ctor_map = HashMap::new();
        for (symbol, reference) in artifact.constructors.iter().enumerate() {
            let key = (reference.origin.clone(), reference.adt_name.clone());
            let decl_id = *decl_index
                .get(&key)
                .ok_or_else(|| "constructor refers to a missing ADT".to_string())?;
            let decl = &merged[decl_id as usize];
            let (ctor_index, constructor) = decl
                .constructors
                .iter()
                .enumerate()
                .find(|(_, (name, _))| *name == reference.name)
                .ok_or_else(|| "constructor missing from its ADT".to_string())?;
            if constructor.1 as u16 != reference.arity {
                return Err("constructor arity mismatch".into());
            }
            let global = bases[&key]
                .checked_add(ctor_index as u16)
                .ok_or_else(|| "constructor id overflow".to_string())?;
            ctor_map.insert(
                u8::try_from(symbol).map_err(|_| "too many constructor symbols".to_string())?,
                global,
            );
        }
        maps.insert(module_id.clone(), (decl_map, ctor_map));
    }

    // Phase 4: function slots. The root comes first so `main` can call module
    // functions directly; dependencies follow in topological order.
    let mut functions: Vec<Rc<TypedProto>> = Vec::new();
    let mut owners: HashMap<String, String> = HashMap::new();
    let mut function_maps: HashMap<String, HashMap<u16, u16>> = HashMap::new();
    let mut function_order: Vec<&String> = Vec::with_capacity(order.len());
    if let Some(root) = order.last() {
        function_order.push(root);
    }
    function_order.extend(order[..order.len().saturating_sub(1)].iter());

    for module_id in function_order {
        let artifact = &modules[module_id];
        let (decl_map, ctor_map) = &maps[module_id];
        let protos = &artifact.module.functions;
        // Assign every global slot first so MK_FUN inside any function can
        // relocate against the complete map.
        let mut function_map: HashMap<u16, u16> = HashMap::new();
        let base =
            u16::try_from(functions.len()).map_err(|_| "too many typed functions".to_string())?;
        for local in 0..protos.len() {
            let local = u16::try_from(local).map_err(|_| "too many typed functions".to_string())?;
            function_map.insert(local, base + local);
        }
        for (_local, proto) in protos.iter().enumerate() {
            if !proto.name.starts_with("<lambda:") {
                if let Some(owner) = owners.insert(proto.name.clone(), module_id.clone()) {
                    return Err(format!(
                        "typed function name collision: '{}' in '{owner}' and '{module_id}'",
                        proto.name
                    ));
                }
            }
            functions.push(remap_proto(proto, decl_map, ctor_map, Some(&function_map))?);
        }
        function_maps.insert(module_id.clone(), function_map);
    }

    let root_artifact = &modules[&root_id];
    let (decl_map, ctor_map) = &maps[&root_id];
    let main = remap_proto(
        &root_artifact.module.main,
        decl_map,
        ctor_map,
        function_maps.get(&root_id),
    )?;
    Ok(TypedModule {
        functions,
        main,
        adt_decls: merged,
    })
}

/// A runtime value of the typed subset.
///
/// `Function` is a plain module function index; `Closure` carries a parent
/// chain. `Cell` is an implementation detail: it lives only in frame registers
/// and closure snapshots for slots shared with lambdas, and every read path
/// (`LOAD_L`, `LOAD_OUTER`, display, equality) unwraps it, so user-visible
/// values are never cells.
#[derive(Clone)]
enum TypedValue {
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
struct TypedClosure {
    index: usize,
    snapshot: Vec<TypedValue>,
    parent: Option<Rc<TypedClosure>>,
}

struct TypedAdt {
    type_: TypedType,
    variant: u16,
    variant_name: Rc<str>,
    payload: Box<[TypedValue]>,
}

/// Snapshot iterator over a List, Tuple, Set, Dict keys or String.
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
    Sorted,
}

fn display_typed(value: &TypedValue) -> String {
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

fn to_value(value: TypedValue) -> TResult<Value> {
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

fn typed_equal(lhs: &TypedValue, rhs: &TypedValue) -> TResult<bool> {
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

fn constant_value(constant: &Constant) -> TResult<TypedValue> {
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

fn typed_contains(container: &TypedValue, value: &TypedValue) -> TResult<bool> {
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

fn typed_slice(
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

fn typed_set_op(op: u32, left: &TypedValue, right: &TypedValue) -> TResult<TypedValue> {
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
fn typed_set_relation(op: u32, left: &TypedValue, right: &TypedValue) -> TResult<bool> {
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
fn typed_list_cmp(left: &TypedValue, right: &TypedValue) -> TResult<i32> {
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

fn typed_list_concat(left: &TypedValue, right: &TypedValue) -> TResult<TypedValue> {
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

fn sort_typed_values(values: &mut [TypedValue]) -> TResult<()> {
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
fn closure_slot<'a>(
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

fn unwrap_cell(value: &TypedValue) -> std::borrow::Cow<'_, TypedValue> {
    match value {
        TypedValue::Cell(cell) => std::borrow::Cow::Owned(cell.borrow().clone()),
        other => std::borrow::Cow::Borrowed(other),
    }
}

fn as_int(value: &TypedValue) -> TResult<&BigInt> {
    match value {
        TypedValue::Int(i) => Ok(i),
        _ => Err("typed opcode expected Int".into()),
    }
}

fn as_index(value: &TypedValue) -> TResult<i64> {
    as_int(value)?
        .to_i64()
        .ok_or_else(|| "integer index is too large".to_string())
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

fn open_iterator(value: &TypedValue) -> TResult<TypedValue> {
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

fn set_insert(items: &mut Vec<TypedValue>, value: TypedValue) -> TResult<()> {
    for item in items.iter() {
        if typed_equal(item, &value)? {
            return Ok(());
        }
    }
    items.push(value);
    Ok(())
}

fn dict_set(
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

fn dict_get(entries: &[(TypedValue, TypedValue)], key: &TypedValue) -> TResult<Option<TypedValue>> {
    for (existing_key, value) in entries.iter() {
        if typed_equal(existing_key, key)? {
            return Ok(Some(value.clone()));
        }
    }
    Ok(None)
}

fn adt_constructor(
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

fn get_item(container: &TypedValue, index: &TypedValue) -> TResult<TypedValue> {
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
const NEW_SET: u32 = 69;
const NEW_DICT: u32 = 70;
const EQ_SET: u32 = 71;
const NE_SET: u32 = 72;
const EQ_DICT: u32 = 73;
const NE_DICT: u32 = 74;
const NEW_ADT: u32 = 75;
const ADT_TAG: u32 = 76;
const ADT_FIELD: u32 = 77;
const EQ_ADT: u32 = 78;
const NE_ADT: u32 = 79;
const TUPLE_ITEM: u32 = 80;
const CONTAINS: u32 = 81;
const SLICE: u32 = 82;
const SET_UNION: u32 = 83;
const SET_INTERSECT: u32 = 84;
const SET_DIFFERENCE: u32 = 85;
const SET_SYMMETRIC: u32 = 86;
const MK_FUN: u32 = 87;
const MK_CLOSURE: u32 = 88;
const LOAD_OUTER: u32 = 89;
const STORE_OUTER: u32 = 90;
const FRESH_CELL: u32 = 91;
const SET_SUBSET: u32 = 92;
const SET_PROPER_SUBSET: u32 = 93;
const SET_SUPERSET: u32 = 94;
const SET_PROPER_SUPERSET: u32 = 95;
const CMP_LIST: u32 = 96;
const LIST_CONCAT: u32 = 97;

pub struct TypedVm {
    functions: Vec<ResolvedProto>,
    main: ResolvedProto,
    adt_decls: Vec<TypedAdtDecl>,
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
        bindings
            .entry("sorted".to_string())
            .or_insert(TypedGlobal::Native(TypedNative::Sorted));
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
        let adt_decls = &self.adt_decls;
        let pool = &mut self.pool;
        let mut frame = pool.acquire(main.proto.register_count as usize);
        let result = execute(main, functions, globals, adt_decls, pool, &mut frame, None);
        pool.release(frame);
        result.and_then(to_value)
    }
}

/// Run one typed proto to completion.
///
/// Register layout is fixed by the compiler: parameters and locals occupy
/// their HIR slots, call arguments are moved into a contiguous window at the
/// callee register, and the result lands in its own register. Jumps use
/// absolute word indices. `closure` is the executing closure, if any; named
/// functions and main pass `None`.
fn execute(
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
                };
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
                registers[a] =
                    TypedValue::Int(BigInt::from(typed_list_cmp(&registers[b], &registers[c])?));
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
                    adt_decls,
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
            let result = execute(
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
            let result = execute(
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
    fn int(value: i64) -> TypedValue {
        TypedValue::Int(BigInt::from(value))
    }

    use super::*;

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
            cells: vec![],
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
        first[0] = int(7);
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
