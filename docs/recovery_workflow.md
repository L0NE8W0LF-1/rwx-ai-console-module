# Recovery workflow

## Overview

The recovery workflow is designed for legitimate diagnostics and maintenance.

1. Connect USB recovery module to the target or test harness.
2. Scan for devices and identify the target.
3. Load or acquire a hardware profile.
4. Run AI compatibility analysis.
5. Select an approved recovery image.
6. Confirm boot and start the recovery environment.
7. Run diagnostics, export logs, and record results.

## Safety constraints

- Read-only metadata access by default
- Explicit user confirmation before boot
- Signed or approved recovery payloads only
- No security bypass or unauthorized firmware flashing
