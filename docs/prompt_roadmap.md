# Prompt Roadmap — Target State and BETA Perimeter

This document replaces earlier roadmap text with a precise, authoritative "target state" for the repository and a strict perimeter for any automated assistant work. Nothing is changed in the codebase until the test-suite is run and results are reported. Follow the rules below exactly: one file per response; non-destructive by default; BETA lock and no-fabrication enforced.

---

CURRENT MODE: BETA (no ALPHA/GAMMA work)

Writable paths (single canonical list):
- scanner/
- tests/
- docs/
- samples/
- ai/gui_dashboard.py
- README.md
- requirements.txt

Everything else is read-only unless the task explicitly names a different writable file.

Safety & non-fabrication rules (mandatory)
- NEVER fabricate: unknown != 0. No field value may be invented; each field MUST include both a `status` and a `source`.
- Never claim success for code that has not been executed.
- If a single test fails twice (two consecutive runs of the same test show failure), STOP and report findings — do not attempt further automated rewrites of modules to fix that test.
- Redact sensitive PII before saving profiles by default: serials, MAC addresses, hostnames. Use `<REDACTED>` and record the redaction in provenance.
- No network access. No executing untrusted binaries outside an isolated container/VM.
- Never use shell=True. Use argument lists and explicit timeouts when calling subprocesses.

Per-response format and limits
- One file per response. Each reply MUST begin with a single-line JSON status object only, then one file block containing the file contents (name=path header). Example first line:
  {"status":"ok","msg":"wrote docs/prompt_roadmap.md"}
- The assistant MUST NOT include multiple files in a single response.
- Keep changes small and focused; large changes should be split into sequential file-by-file responses, each with tests that run and report.

Token and size constraints
- Do not assume a fixed token budget for all operations. Instead: one file per response, and keep file content reasonable (prefer incremental PRs). If a requested file is large, return a short summary and ask for permission to continue in smaller chunks.

Target state (what we are building)
- Core (first path): a testable, GUI-free scanner controller and core models:
  - scanner/model.py — dataclasses with per-field status and source.
  - scanner/adapter.py — HostAdapter contract.
  - scanner/registry.py — adapter registry.
  - scanner/orchestrator.py — GUI-free controller that orchestrates discovery and diagnostics; testable headlessly.
- Logging & IO:
  - scanner/structured_log.py — JSONL logger (thread-safe), does not call logging.basicConfig.
  - scanner/profile_io.py — validator + strict save (no-clobber by default) and explicit overwrite semantics.
- Adapters (in order):
  1. Mock adapter (for unit tests) — proves the core path.
  2. Generic host adapter (platform/os/shutil only) — non-destructive, read-only enumerations.
  3. Declared-profile adapter — wraps legacy profiles and marks results `user-declared` (never `detected`). Regression test pinned to the baseline scores.
  4. OS-specific adapter for host (e.g., linux-proc) — best-effort, read-only enumerations of GPUs/disks when permitted.
- GUI: thin shim. The GUI must not contain scan logic. It calls the orchestrator/controller asynchronously, using a queue.Queue for worker→GUI events and root.after polling to update widgets. No Tk widgets are touched from worker threads.

Validation, schema and sample profiles
- Profiles are validated with a strict JSON schema. Required top-level fields:
  - `schema_version` (string)
  - `scan_id` (string)
  - `profile_name` (optional but recommended)
  - `device_family` (string)
  - `platform` (string)
  - `model` (string)

- Every field stored in `fields` MUST be an object containing:
  - `value`: may be null if unknown
  - `status`: one of ["detected","unknown","unavailable","unsupported","denied","failed","user-declared"]
  - `source`: string (e.g., "user-declared", "generic-host", "linux-proc")

- Missing numeric values must not be coerced to 0. If numeric value is a string it may be normalized to a number only if the string is an unambiguous numeric literal; otherwise it must remain as-is and status=failed or unknown.

- When saving profiles: default behavior is NO-CLOBBER — refuse to overwrite if target exists. Arguments: overwrite=False (refuse), overwrite=True (create backup *.bak.TIMESTAMP then replace), or name_by_scanid=True to write <basename>.<scan_id>.json.

Regression and baseline
- Before changing any scoring code (spec_detection or local AI engine), run and pin baseline scores from samples/*.json. Use a deterministic sample glob with explicit filename→expected mapping. Do not rely on OS glob ordering: key by filename.
- The regression test MUST map expected scores by filename (e.g., {"xbox-series-s.json":1.0, "playstation-5.json":0.96, "nintendo-switch.json":0.96}). Run and record the baseline pass before any code edits.

Executor, license, and safety
- License detection is NOT a safety gate by default. Do not block execution because a file lacks a license header. The executor should: (a) detect license from content without re-reading the file (pass content into detect_license), (b) report license metadata, and (c) allow callers to enforce policies externally.
- Fixes to executor behavior (short-term): remove logging.basicConfig from constructor; accept an explicit `allow_unknown_license` flag; implement detect_license_from_content(content) to avoid recursion; use subprocess.run with argument lists, a controlled temp working dir, and a timeout; do not claim the sandbox provides security — recommend containers/VMs in docs.

Threading and GUI
- Worker threads must NOT touch Tk widgets. Use queue.Queue for events; GUI polls queue with root.after and applies updates on the main thread. The orchestrator is GUI-free and testable in CI.

BETA mode lock and no-fabrication rule
- Implement a BETA-mode lock that the operator sets; when BETA lock is enabled, disallow destructive actions (write_profile, boot_recovery) unless explicitly permitted.
- Distinguish and report mocked vs physical validation in diagnostics results (field-level metadata: `detected_by: "mock"|"adapter-id"`).

Redaction and privacy
- When saving profiles, redact serial numbers, MAC addresses, and hostnames by default. The saved profile MUST document which fields were redacted in `provenance.redaction`.

Requirements and tested Python
- requirements.txt must include: PyYAML
- Document the tested Python runtime: Python 3.12.3 in README and requirements sections.

Roadmap Phases 1–6 (BETA)
- Phase 1 (Core + Mock): scanner.model, adapter contract, registry, orchestrator (GUI-free controller), mock adapter, unit tests proving discover/run_scan. Tests must run and pass before further changes.
- Phase 2 (Host adapter): generic-host adapter (platform/os/shutil only), profile_io validator + no-clobber save, JSONL logger.
- Phase 3 (Declared legacy): declared-profile adapter, regression tests pinned to baseline sample scores (by filename). GUI remains a shim.
- Phase 4 (OS adapters): OS-specific adapter(s) (linux-proc), enumeration of multiple GPUs/disks; best-effort reads only.
- Phase 5 (GUI hook): thin GUI shim; queue-based updates; GUI acceptance tests are manual or run in environments with tkinter available.
- Phase 6 (Ops & docs BETA closeout): finalize docs, tests, and explicit operator procedures. (Production containers/plugin work moved OUT of BETA.)

Note: container/VM-based sandboxing and plugin frameworks are out of scope for BETA; they belong to a later track (Ops/production).

Stop rule
- If a failing test repeats twice across attempts, stop automated changes and produce a human-readable report (test name, failure count, failing trace snippet) and recommended manual next steps.

Acceptance and change workflow (strict)
1. Implement one file change + tests under scanner/ or tests/ only.
2. Run tests locally (unittest) and produce a JSON test report: {"passed":bool,"total":N,"failures":[...]}.
3. If tests pass, commit and proceed to the next file. If a test fails, run it once more; if it fails again, STOP and report.
4. GUI changes: do not attempt headless GUI tests in CI by default. Provide a GUI-free controller and unit tests for the controller.

Developer instructions for assistant responses
- Every assistant response must start with a single-line JSON status: {"status":"ok|error|refused","msg":"short"}
- After the JSON line, include exactly one file block (if providing code) in the format name=path and the full file contents.
- If refusing an operation because it violates the BETA lock, return: {"status":"refused","msg":"banned_write: <path>"} and no file block.

Closing notes
- This document is the authoritative, corrected roadmap and perimeter. Implementations must follow the ordered phases and the non-fabrication rule strictly. Ask for explicit permission to proceed file-by-file; changes will only be applied after tests for the changed file have been run and reported.
