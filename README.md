# USB Activity Monitor

A Linux-based USB activity monitoring project for SOC Analyst
portfolio and endpoint security learning.

## Project Overview

This tool monitors USB device insertion and removal events on Linux.
It records device metadata when available and compares device serial
numbers against a local authorization allowlist.

## Features

- Monitor USB device add/remove events
- Record timestamps and monitoring account
- Capture vendor ID, product ID and serial number when available
- Classify devices using an authorized serial-number allowlist
- Generate console alerts for devices not in the allowlist
- Flag devices with missing serial numbers for review
- Store events in JSON Lines format
- Generate a summary report from available event logs
- Include automated tests for allowlist classification

## Technology Stack

- Python
- pyudev
- Linux udev
- JSON Lines
- CSV
- unittest

<img width="1254" height="1254" alt="USB Activity Monitor Shield" src="https://github.com/user-attachments/assets/a98483a6-4807-4663-986f-0a00ef81bf5f" />  

## Project Structure

```text
usb-activity-monitor/
├── monitor.py
├── report.py
├── allowed_serials.txt
├── requirements.txt
├── .gitignore
└── tests/
    └── test_monitor.py


