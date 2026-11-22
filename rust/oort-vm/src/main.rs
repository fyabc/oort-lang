//! oort-vm: spike register VM consuming `.obc` bytecode (spec 13).
//!
//! Usage: oort-vm <file.obc>
//! Both kind=0 (type-erased) and kind=1 (typed scalar subset) files are
//! accepted; the kind byte selects the reader and VM.
//! Program `print` output goes to stdout; the final value is reported on stderr
//! (prefixed `value:`) for differential comparison. Errors exit non-zero.

// The spike parses the full .obc format but only executes a Phase 0 subset, so
// many descriptor fields are intentionally unused for now.
#![allow(dead_code)]

mod obc;
mod typed;
mod vm;

use std::process::ExitCode;

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        eprintln!("usage: oort-vm <file.obc>");
        return ExitCode::from(2);
    }
    let data = match std::fs::read(&args[1]) {
        Ok(d) => d,
        Err(e) => {
            eprintln!("cannot read {}: {e}", args[1]);
            return ExitCode::from(2);
        }
    };
    let kind = data.get(3).copied().unwrap_or(255);
    let result = match kind {
        0 => match obc::read_module(&data) {
            Ok(module) => vm::Vm::new(module).run_main(),
            Err(e) => Err(format!("bytecode error: {e}")),
        },
        1 => match typed::read_typed_module(&data) {
            Ok(module) => typed::TypedVm::new(module).run_main(),
            Err(e) => Err(format!("typed bytecode error: {e}")),
        },
        _ => Err(format!("unsupported bytecode kind: {kind}")),
    };
    match result {
        Ok(value) => {
            eprintln!("value: {}", vm::display(&value));
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("runtime error: {e}");
            ExitCode::from(1)
        }
    }
}
