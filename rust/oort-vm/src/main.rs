//! oort-vm: spike register VM consuming `.obc` bytecode (spec 13).
//!
//! Usage: oort-vm <file.obc>
//! kind=0 (type-erased), kind=1 (typed scalar subset) and kind=2 (linked
//! typed bundle) files are accepted; the kind byte selects the reader and VM.
//! Program `print` output goes to stdout; the final value is reported on stderr
//! (prefixed `value:`) for differential comparison. Errors use the standard
//! `file:line:col: error: ...` header plus `note: called from ...` frames and
//! exit non-zero.

// The spike parses the full .obc format but only executes a Phase 0 subset, so
// many descriptor fields are intentionally unused for now.
#![allow(dead_code)]

mod obc;
mod typed;
mod vm;

use std::process::ExitCode;

fn read(path: &str) -> Result<Vec<u8>, String> {
    std::fs::read(path).map_err(|e| format!("error: cannot read {path}: {e}"))
}

fn link_mode(args: &[String]) -> Result<vm::Value, String> {
    if args.len() < 4 {
        return Err("usage: oort-vm --link <root.obc> <dependency.obc>...".into());
    }
    let root = typed::read_typed_artifact(&read(&args[2])?)
        .map_err(|e| format!("error: typed artifact: {e}"))?;
    let mut dependencies = Vec::new();
    for path in &args[3..] {
        dependencies.push(
            typed::read_typed_artifact(&read(path)?)
                .map_err(|e| format!("error: typed artifact: {e}"))?,
        );
    }
    let module =
        typed::link_artifacts(root, dependencies).map_err(|e| format!("error: typed link: {e}"))?;
    typed::TypedVm::new(module).run_main()
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!("usage: oort-vm <file.obc> | oort-vm --link <root.obc> <dependency.obc>...");
        return ExitCode::from(2);
    }
    let result = if args[1] == "--link" {
        link_mode(&args)
    } else {
        if args.len() != 2 {
            eprintln!("usage: oort-vm <file.obc> | oort-vm --link <root.obc> <dependency.obc>...");
            return ExitCode::from(2);
        }
        let data = match read(&args[1]) {
            Ok(d) => d,
            Err(e) => {
                eprintln!("{e}");
                return ExitCode::from(2);
            }
        };
        let kind = data.get(3).copied().unwrap_or(255);
        match kind {
            0 => match obc::read_module(&data) {
                Ok(module) => vm::Vm::new(module).run_main(),
                Err(e) => Err(format!("error: bytecode: {e}")),
            },
            1 => match typed::read_typed_module(&data) {
                Ok(module) => typed::TypedVm::new(module).run_main(),
                Err(e) => Err(format!("error: typed bytecode: {e}")),
            },
            2 => match typed::read_linked_bundle(&data) {
                Ok(module) => typed::TypedVm::new(module).run_main(),
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
