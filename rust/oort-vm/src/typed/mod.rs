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
//! - `mod.rs`: shared types and public re-exports;
//! - `decode.rs`: proto / bundle / artifact decoding;
//! - `link.rs`: module artifact linker (import checks, ADT merge, id relocation);
//! - `value.rs`: runtime values and opcode helpers;
//! - `opcodes.rs`: typed opcode numbers;
//! - `vm.rs`: globals, frame pool, `execute` and the opcode dispatch loop.

pub(crate) type TResult<T> = Result<T, String>;

mod decode;
mod link;
mod opcodes;
mod value;
mod vm;

pub use decode::{read_linked_bundle, read_typed_artifact, read_typed_module};
pub use link::link_artifacts;
pub use vm::TypedVm;

use std::rc::Rc;

use crate::obc::Constant;

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
