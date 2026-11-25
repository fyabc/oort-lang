//! Typed proto / bundle / artifact decoding (spec 14, design 19).

use std::rc::Rc;

use crate::obc::Reader;

use super::{
    TResult, TypedAdtDecl, TypedArtifact, TypedConstructorRef, TypedExport, TypedImport,
    TypedModule, TypedProto, TypedType,
};

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
    // Diagnostic table; kept so runtime errors can point at source lines.
    let (filename, positions) = r.source_positions()?;
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
        positions,
        filename,
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
