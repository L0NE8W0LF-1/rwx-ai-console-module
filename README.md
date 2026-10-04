# RWX AI Console Recovery Module

A local AI-powered USB recovery and diagnostic platform for authorized hardware diagnostics, console repair workflows, and recovery boot environments.

This project is intentionally scoped to legitimate repair and development use cases:
- read hardware metadata and system state
- detect device model/revision and boot status
- load a signed recovery or diagnostic boot environment
- provide AI-assisted diagnostics and compatibility research
- support multiple console families via interchangeable adapters

## Safety and scope

This repository focuses on safe, authorized workflows:
- repair diagnostics
- hardware identification
- safe bootloader-based recovery
- developer recovery environments
- engineering compatibility research

It explicitly excludes:
- bypassing platform security
- unauthorized firmware modification
- disabling protections or anti-tamper logic
- piracy, DRM circumvention, or exploitation

## Project goals

- Create a USB-connected hardware recovery module that can be plugged into a target console or test bench
- Read safe hardware metadata and identify the target platform and revision
- Use an embedded/local AI layer to analyze hardware data and suggest recovery paths
- Support a safe recovery bootloader for maintenance and diagnostics
- Maintain a compatibility matrix for supported hardware families and adapters

## Repository layout

- `ai/` — local AI logic, profile analysis, and GUI
- `app/` — local desktop app and control logic
- `docs/` — architecture, recovery workflow, and design docs
- `firmware/` — recovery bootloader and embedded firmware stubs
- `samples/` — example hardware profiles

## Running the local AI analysis

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ai/spec_detection.py --profile samples/xbox-series-s.json
```

## Launching the GUI

```bash
python ai/gui_dashboard.py
```

## Current status

This repository is a starter implementation and architecture scaffold for a legitimate recovery/debugging project.
