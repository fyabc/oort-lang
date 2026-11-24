//! Typed module artifact linker: import checks, ADT merge and id relocation.

use std::collections::HashMap;
use std::rc::Rc;

use super::opcodes::{DEF_FUN, MK_CLOSURE, MK_FUN, NEW_ADT};
use super::{
    TResult, TypedAdtDecl, TypedArtifact, TypedExport, TypedModule, TypedProto, TypedType,
};

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
