# RWX AI Console Recovery Module

This project is a local GUI and AI-powered USB recovery/debugging system for authorized device diagnostics and safe recovery workflows.

## Overview

The module is designed to:
- detect connected devices and read safe metadata
- analyze hardware profiles with a local AI engine
- propose recovery options and compatibility recommendations
- let a user launch a recovery image from a bootloader workflow
- record logs and export reports

## Components

- `ai/spec_detection.py` — profile scoring and recommendations
- `ai/local_ai_engine.py` — AI-style analysis engine
- `ai/gui_dashboard.py` — Tkinter GUI dashboard
- `app/` — application and boot logic scaffolding
- `docs/` — design and workflow documentation
- `samples/` — sample hardware profiles
