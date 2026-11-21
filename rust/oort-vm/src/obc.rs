//! Reader for the `.obc` bytecode format (spec 13). Little-endian, tagged
//! constant pool. Mirrors `oort_lang.bytecode.serialize`.

use std::rc::Rc;

#[derive(Debug, Clone)]
pub enum Constant {
    Null,
    Bool(bool),
    Int(i64),
    Float(f64),
    Str(Rc<str>),
    Slots(Vec<u16>),
    Class(ClassSpec),
    Call(CallSpec),
    Enum(EnumSpec),
    Match(MatchSpec),
    Import(ImportSpec),
    Extension(ExtensionSpec),
}

#[derive(Debug, Clone)]
pub struct ClassSpec {
    pub name: String,
    pub base_count: u16,
    pub methods: Vec<(String, u32)>,
    pub slots: Vec<(String, bool, Option<u32>)>,
    pub class_methods: Vec<(String, u32)>,
    pub operators: Vec<(String, u16, u32)>,
    pub has_metaclass: bool,
}

#[derive(Debug, Clone)]
pub struct CallSpec {
    pub positional_count: u16,
    pub keywords: Vec<String>,
    pub has_block: bool,
}

#[derive(Debug, Clone)]
pub struct EnumSpec {
    pub name: String,
    pub constructors: Vec<(String, u16)>,
}

#[derive(Debug, Clone)]
pub struct Pattern {
    pub kind: u8,
    pub name: String,
    pub args: Vec<Pattern>,
}

#[derive(Debug, Clone)]
pub struct MatchSpec {
    pub arms: Vec<(Pattern, u32)>,
}

#[derive(Debug, Clone)]
pub struct ImportSpec {
    pub module_path: String,
    pub alias: Option<String>,
    pub names: Vec<(String, Option<String>)>,
    pub is_from: bool,
}

#[derive(Debug, Clone)]
pub struct ExtensionSpec {
    pub name: String,
    pub function_index: u32,
    pub symbol: Option<String>,
    pub operand_count: u16,
    pub receiver_name: String,
}

#[derive(Debug, Clone)]
pub struct ParamSpec {
    pub name: String,
    pub kind: u8,
    pub slot: u16,
    pub has_default: bool,
    pub default_index: Option<u32>,
}

#[derive(Debug, Clone)]
pub struct Signature {
    pub has_this: bool,
    pub params: Vec<ParamSpec>,
}

#[derive(Debug, Clone)]
pub struct Proto {
    pub name: String,
    pub params: Vec<String>,
    pub register_count: u16,
    pub local_count: u16,
    pub scratch_base: u16,
    pub has_this: bool,
    pub uses_cells: bool,
    pub defines_extensions: bool,
    pub signature: Signature,
    pub code: Vec<u32>,
    pub constants: Vec<Constant>,
}

#[derive(Debug, Clone)]
pub struct Module {
    pub functions: Vec<Rc<Proto>>,
    pub main: Rc<Proto>,
}

pub struct Reader<'a> {
    data: &'a [u8],
    pos: usize,
}

type RResult<T> = Result<T, String>;

impl<'a> Reader<'a> {
    pub fn new(data: &'a [u8]) -> Self {
        Reader { data, pos: 0 }
    }

    fn take(&mut self, n: usize) -> RResult<&'a [u8]> {
        if self.pos + n > self.data.len() {
            return Err("unexpected end of bytecode file".into());
        }
        let chunk = &self.data[self.pos..self.pos + n];
        self.pos += n;
        Ok(chunk)
    }

    pub fn u8(&mut self) -> RResult<u8> {
        Ok(self.take(1)?[0])
    }
    pub fn u16(&mut self) -> RResult<u16> {
        let b = self.take(2)?;
        Ok(u16::from_le_bytes([b[0], b[1]]))
    }
    pub fn u32(&mut self) -> RResult<u32> {
        let b = self.take(4)?;
        Ok(u32::from_le_bytes([b[0], b[1], b[2], b[3]]))
    }
    pub fn i32(&mut self) -> RResult<i32> {
        let b = self.take(4)?;
        Ok(i32::from_le_bytes([b[0], b[1], b[2], b[3]]))
    }
    pub fn i64(&mut self) -> RResult<i64> {
        let b = self.take(8)?;
        Ok(i64::from_le_bytes(b.try_into().unwrap()))
    }
    pub fn f64(&mut self) -> RResult<f64> {
        let b = self.take(8)?;
        Ok(f64::from_le_bytes(b.try_into().unwrap()))
    }
    pub fn boolean(&mut self) -> RResult<bool> {
        Ok(self.u8()? != 0)
    }
    pub fn string(&mut self) -> RResult<String> {
        let len = self.u32()? as usize;
        let bytes = self.take(len)?;
        String::from_utf8(bytes.to_vec()).map_err(|_| "invalid UTF-8 in bytecode".into())
    }
    pub fn rc_str(&mut self) -> RResult<Rc<str>> {
        Ok(Rc::from(self.string()?.as_str()))
    }
    pub fn opt_string(&mut self) -> RResult<Option<String>> {
        if self.boolean()? {
            Ok(Some(self.string()?))
        } else {
            Ok(None)
        }
    }
    pub fn opt_u32(&mut self) -> RResult<Option<u32>> {
        if self.boolean()? {
            Ok(Some(self.u32()?))
        } else {
            Ok(None)
        }
    }

    fn pattern(&mut self) -> RResult<Pattern> {
        let kind = self.u8()?;
        let name = self.string()?;
        let n = self.u32()?;
        let mut args = Vec::with_capacity(n as usize);
        for _ in 0..n {
            args.push(self.pattern()?);
        }
        Ok(Pattern { kind, name, args })
    }

    fn constant(&mut self) -> RResult<Constant> {
        let tag = self.u8()?;
        Ok(match tag {
            0 => Constant::Null,
            1 => Constant::Bool(self.boolean()?),
            2 => Constant::Int(self.i64()?),
            3 => Constant::Float(self.f64()?),
            4 => Constant::Str(self.rc_str()?),
            5 => {
                let n = self.u32()?;
                let mut slots = Vec::with_capacity(n as usize);
                for _ in 0..n {
                    slots.push(self.u16()?);
                }
                Constant::Slots(slots)
            }
            10 => {
                let name = self.string()?;
                let base_count = self.u16()?;
                let methods = self.name_index_pairs()?;
                let ns = self.u32()?;
                let mut slots = Vec::with_capacity(ns as usize);
                for _ in 0..ns {
                    slots.push((self.string()?, self.boolean()?, self.opt_u32()?));
                }
                let class_methods = self.name_index_pairs()?;
                let no = self.u32()?;
                let mut operators = Vec::with_capacity(no as usize);
                for _ in 0..no {
                    operators.push((self.string()?, self.u16()?, self.u32()?));
                }
                let has_metaclass = self.boolean()?;
                Constant::Class(ClassSpec {
                    name,
                    base_count,
                    methods,
                    slots,
                    class_methods,
                    operators,
                    has_metaclass,
                })
            }
            11 => {
                let positional_count = self.u16()?;
                let nk = self.u32()?;
                let mut keywords = Vec::with_capacity(nk as usize);
                for _ in 0..nk {
                    keywords.push(self.string()?);
                }
                let has_block = self.boolean()?;
                Constant::Call(CallSpec {
                    positional_count,
                    keywords,
                    has_block,
                })
            }
            12 => {
                let name = self.string()?;
                let nc = self.u32()?;
                let mut constructors = Vec::with_capacity(nc as usize);
                for _ in 0..nc {
                    constructors.push((self.string()?, self.u16()?));
                }
                Constant::Enum(EnumSpec { name, constructors })
            }
            13 => {
                let na = self.u32()?;
                let mut arms = Vec::with_capacity(na as usize);
                for _ in 0..na {
                    arms.push((self.pattern()?, self.u32()?));
                }
                Constant::Match(MatchSpec { arms })
            }
            15 => {
                let module_path = self.string()?;
                let alias = self.opt_string()?;
                let nn = self.u32()?;
                let mut names = Vec::with_capacity(nn as usize);
                for _ in 0..nn {
                    names.push((self.string()?, self.opt_string()?));
                }
                let is_from = self.boolean()?;
                Constant::Import(ImportSpec {
                    module_path,
                    alias,
                    names,
                    is_from,
                })
            }
            16 => {
                let name = self.string()?;
                let function_index = self.u32()?;
                let symbol = self.opt_string()?;
                let operand_count = self.u16()?;
                let receiver_name = self.string()?;
                Constant::Extension(ExtensionSpec {
                    name,
                    function_index,
                    symbol,
                    operand_count,
                    receiver_name,
                })
            }
            _ => return Err(format!("unknown constant pool tag: {tag}")),
        })
    }

    fn name_index_pairs(&mut self) -> RResult<Vec<(String, u32)>> {
        let n = self.u32()?;
        let mut out = Vec::with_capacity(n as usize);
        for _ in 0..n {
            out.push((self.string()?, self.u32()?));
        }
        Ok(out)
    }

    fn signature(&mut self) -> RResult<Signature> {
        let has_this = self.boolean()?;
        let n = self.u32()?;
        let mut params = Vec::with_capacity(n as usize);
        for _ in 0..n {
            params.push(ParamSpec {
                name: self.string()?,
                kind: self.u8()?,
                slot: self.u16()?,
                has_default: self.boolean()?,
                default_index: self.opt_u32()?,
            });
        }
        Ok(Signature { has_this, params })
    }

    fn proto(&mut self) -> RResult<Proto> {
        let name = self.string()?;
        let np = self.u32()?;
        let mut params = Vec::with_capacity(np as usize);
        for _ in 0..np {
            params.push(self.string()?);
        }
        let register_count = self.u16()?;
        let local_count = self.u16()?;
        let scratch_base = self.u16()?;
        let flags = self.u8()?;
        let signature = self.signature()?;
        let nc = self.u32()?;
        let mut code = Vec::with_capacity(nc as usize);
        for _ in 0..nc {
            code.push(self.u32()?);
        }
        let nk = self.u32()?;
        let mut constants = Vec::with_capacity(nk as usize);
        for _ in 0..nk {
            constants.push(self.constant()?);
        }
        // Positions are optional and only used for diagnostics; skip them.
        if self.boolean()? {
            let _filename = self.string()?;
            let npos = self.u32()?;
            for _ in 0..npos {
                let _line = self.u32()?;
                let _column = self.i32()?;
            }
        }
        Ok(Proto {
            name,
            params,
            register_count,
            local_count,
            scratch_base,
            has_this: flags & 1 != 0,
            uses_cells: flags & 2 != 0,
            defines_extensions: flags & 4 != 0,
            signature,
            code,
            constants,
        })
    }
}

pub fn read_module(data: &[u8]) -> RResult<Module> {
    let mut r = Reader::new(data);
    if r.take(3)? != b"OBC" {
        return Err("not an Oort bytecode file (bad magic)".into());
    }
    let kind = r.u8()?;
    if kind != 0 {
        return Err(format!("unsupported bytecode kind: {kind}"));
    }
    let version = r.u8()?;
    if version != 1 {
        return Err(format!("unsupported bytecode version: {version}"));
    }
    let nf = r.u32()?;
    let mut functions = Vec::with_capacity(nf as usize);
    for _ in 0..nf {
        functions.push(Rc::new(r.proto()?));
    }
    let main = Rc::new(r.proto()?);
    Ok(Module { functions, main })
}
