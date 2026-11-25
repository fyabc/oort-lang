//! oort-vm: spike register VM consuming `.obc` bytecode (spec 13).
//!
//! Usage: oort-vm [--trace] <file.obc>
//!        oort-vm [--trace] --link <root.obc> <dependency.obc>...
//!        oort-vm --disasm <file.obc> | --disasm --link ...
//! kind=0 (type-erased), kind=1 (typed scalar subset) and kind=2 (linked
//! typed bundle) files are accepted; the kind byte selects the reader and VM.
//! Program `print` output goes to stdout; the final value is reported on stderr
//! (prefixed `value:`) for differential comparison. `--trace` writes one line
//! per executed instruction to stderr; `--disasm` prints the artifact instead
//! of running it. Errors use the standard `file:line:col: error: ...` header
//! plus `note: called from ...` frames and exit non-zero.

// The spike parses the full .obc format but only executes a Phase 0 subset, so
// many descriptor fields are intentionally unused for now.
#![allow(dead_code)]

mod disasm;
mod obc;
mod opcodes;
mod typed;
mod vm;

use std::process::ExitCode;

fn read(path: &str) -> Result<Vec<u8>, String> {
    std::fs::read(path).map_err(|e| format!("error: cannot read {path}: {e}"))
}

fn usage() {
    eprintln!("usage: oort-vm [--trace] <file.obc>");
    eprintln!("       oort-vm [--trace] --link <root.obc> <dependency.obc>...");
    eprintln!("       oort-vm --disasm <file.obc> | --disasm --link <root.obc> ...");
}

fn load_linked(args: &[String]) -> Result<typed::TypedModule, String> {
    if args.len() < 3 {
        return Err("usage: oort-vm [--trace] --link <root.obc> <dependency.obc>...".to_string());
    }
    let root = typed::read_typed_artifact(&read(&args[1])?)
        .map_err(|e| format!("error: typed artifact: {e}"))?;
    let mut dependencies = Vec::new();
    for path in &args[2..] {
        dependencies.push(
            typed::read_typed_artifact(&read(path)?)
                .map_err(|e| format!("error: typed artifact: {e}"))?,
        );
    }
    typed::link_artifacts(root, dependencies).map_err(|e| format!("error: typed link: {e}"))
}

fn link_mode(args: &[String], trace: bool) -> Result<vm::Value, String> {
    let module = load_linked(args)?;
    let mut vm = typed::TypedVm::new(module);
    vm.set_trace(trace);
    vm.run_main()
}

fn disasm_mode(args: &[String]) -> Result<(), String> {
    if args[0] == "--link" {
        let module = load_linked(args)?;
        println!("{}", disasm::disassemble_typed(&module));
        return Ok(());
    }
    let data = read(&args[0])?;
    let kind = data.get(3).copied().unwrap_or(255);
    match kind {
        0 => {
            let module = obc::read_module(&data).map_err(|e| format!("error: bytecode: {e}"))?;
            println!("{}", disasm::disassemble_dynamic(&module));
        }
        1 => {
            let module = typed::read_typed_module(&data)
                .map_err(|e| format!("error: typed bytecode: {e}"))?;
            println!("{}", disasm::disassemble_typed(&module));
        }
        2 => {
            let module = typed::read_linked_bundle(&data)
                .map_err(|e| format!("error: linked bundle: {e}"))?;
            println!("{}", disasm::disassemble_typed(&module));
        }
        _ => return Err(format!("error: unsupported bytecode kind: {kind}")),
    }
    Ok(())
}

fn main() -> ExitCode {
    let mut args: Vec<String> = std::env::args().skip(1).collect();
    let trace = args.iter().any(|arg| arg == "--trace");
    let disasm = args.iter().any(|arg| arg == "--disasm");
    args.retain(|arg| arg != "--trace" && arg != "--disasm");
    if args.is_empty() {
        usage();
        return ExitCode::from(2);
    }
    if args[0] == "--link" {
        if args.len() < 3 {
            usage();
            return ExitCode::from(2);
        }
    } else if args.len() != 1 {
        usage();
        return ExitCode::from(2);
    }
    if disasm {
        return match disasm_mode(&args) {
            Ok(()) => ExitCode::SUCCESS,
            Err(e) => {
                eprintln!("{e}");
                ExitCode::from(1)
            }
        };
    }
    let result = if args[0] == "--link" {
        link_mode(&args, trace)
    } else {
        let data = match read(&args[0]) {
            Ok(d) => d,
            Err(e) => {
                eprintln!("{e}");
                return ExitCode::from(2);
            }
        };
        let kind = data.get(3).copied().unwrap_or(255);
        match kind {
            0 => match obc::read_module(&data) {
                Ok(module) => {
                    let mut vm = vm::Vm::new(module);
                    vm.set_trace(trace);
                    vm.run_main()
                }
                Err(e) => Err(format!("error: bytecode: {e}")),
            },
            1 => match typed::read_typed_module(&data) {
                Ok(module) => {
                    let mut vm = typed::TypedVm::new(module);
                    vm.set_trace(trace);
                    vm.run_main()
                }
                Err(e) => Err(format!("error: typed bytecode: {e}")),
            },
            2 => match typed::read_linked_bundle(&data) {
                Ok(module) => {
                    let mut vm = typed::TypedVm::new(module);
                    vm.set_trace(trace);
                    vm.run_main()
                }
                Err(e) => Err(format!("error: linked bundle: {e}")),
            },
            _ => Err(format!("error: unsupported bytecode kind: {kind}")),
        }
    };
    match result {
        Ok(value) => {
            eprintln!("value: {}", vm::display(&value));
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("{e}");
            ExitCode::from(1)
        }
    }
}
