# Security Policy

## Supported versions

Oort is an early-stage project. Only the latest `main` branch and the most recent
release receive fixes. Version `0.2.x` is experimental and should not be used
where untrusted input is executed.

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Use GitHub's private vulnerability reporting:

1. Go to the repository's **Security** tab.
2. Choose **Report a vulnerability**.
3. Include a minimal `.ort` reproducer, the command used, and the observed
   behavior.

We will acknowledge the report, investigate, and coordinate a fix and disclosure
timeline with you.

## Scope notes

The interpreter executes Oort source code with the privileges of the Python
process. Running untrusted `.ort` files is equivalent to running untrusted
Python code; there is no sandbox. Reports about that design are out of scope,
but parser crashes, unbounded resource use reachable from a file, and
diagnostic-path information leaks are in scope.
