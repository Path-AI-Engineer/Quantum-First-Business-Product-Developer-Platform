# Time-to-first-success protocol

Twelve clean-environment fixtures execute: setup, start sandbox, create organization/project/key, list capabilities, submit a local job through each SDK, wait, and verify the artifact digest. Timings are deterministic laboratory measurements, not external-user research.

Targets:

- clone-to-first-success median at or below 15 minutes;
- SDK-to-first-success median at or below 10 minutes after sandbox readiness;
- every expected failure returns code, message, correlation ID, and remediation hint;
- Python/TypeScript golden-path names and behavior remain equivalent.

The generated report records synthetic automated runs. It must not be presented as 12 independent human usability sessions.

