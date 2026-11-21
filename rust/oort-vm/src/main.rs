//! oort-vm: spike register VM consuming `.obc` bytecode (spec 13).
//!
//! Usage: oort-vm <file.obc>
//! Program `print` output goes to stdout; the final value is reported on stderr
//! (prefixed `value:`) for differential comparison. Errors exit non-zero.

// The spike parses the full .obc format but only executes a Phase 0 subset, so
// many descriptor fields are intentionally unused for now.
#![allow(dead_code)]

mod obc;
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
    let module = match obc::read_module(&data) {
        Ok(m) => m,
        Err(e) => {
            eprintln!("bytecode error: {e}");
            return ExitCode::from(1);
        }
    };
    let mut machine = vm::Vm::new(module);
    match machine.run_main() {
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
