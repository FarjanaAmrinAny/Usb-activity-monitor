import getpass
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pyudev

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "usb_events.jsonl"
ALLOWLIST_FILE = BASE_DIR / "allowed_serials.txt"

# Console alerts are enabled by default.
ALERT_UNAUTHORIZED = True


def read_attribute(device, name):
    """Read a sysfs device attribute safely."""
    try:
        value = device.attributes.get(name)
        return value.decode("utf-8", errors="replace") if value else None
    except (OSError, AttributeError):
        return None


def get_monitor_user():
    """Record the account that started the monitor."""
    return os.environ.get("SUDO_USER") or getpass.getuser()


def load_allowed_serials():
    """Load authorized serial numbers from a local allowlist."""
    if not ALLOWLIST_FILE.exists():
        return set()

    return {
        line.strip()
        for line in ALLOWLIST_FILE.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def classify_device(serial, allowed_serials):
    if not allowed_serials:
        return "UNKNOWN", "Allowlist is empty or not configured"

    if not serial:
        return "REVIEW", "Device serial number is unavailable"

    if serial in allowed_serials:
        return "AUTHORIZED", "Serial number matches allowlist"

    return "UNAUTHORIZED", "Serial number is not in allowlist"


def log_event(event):
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")


def main():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="usb")

    print("USB Activity Monitor started.")
    print(f"Log file: {LOG_FILE}")
    print("Press Ctrl+C to stop.")

    try:
        for device in monitor:
            if device.action not in {"add", "remove"}:
                continue

            # Ignore interfaces; record whole USB devices only.
            if device.device_type != "usb_device":
                continue

            serial = (
                device.get("ID_SERIAL_SHORT")
                or read_attribute(device, "serial")
            )
            vendor_id = (
                device.get("ID_VENDOR_ID")
                or read_attribute(device, "idVendor")
            )
            product_id = (
                device.get("ID_MODEL_ID")
                or read_attribute(device, "idProduct")
            )

            allowed = load_allowed_serials()
            status, reason = classify_device(serial, allowed)

            event = {
                "timestamp": datetime.now().astimezone().isoformat(
                    timespec="seconds"
                ),
                "action": device.action,
                "monitor_user": get_monitor_user(),
                "device_path": device.sys_path,
                "vendor_id": vendor_id,
                "product_id": product_id,
                "manufacturer": (
                    device.get("ID_VENDOR")
                    or read_attribute(device, "manufacturer")
                ),
                "product": (
                    device.get("ID_MODEL")
                    or read_attribute(device, "product")
                ),
                "serial_number": serial,
                "authorization_status": status,
                "reason": reason,
            }

            log_event(event)

            print(json.dumps(event, indent=2, ensure_ascii=False))

            if (
                device.action == "add"
                and status == "UNAUTHORIZED"
                and ALERT_UNAUTHORIZED
            ):
                print(
                    "\n[ALERT] USB device serial is not in the allowlist!\n"
                )
            elif device.action == "add" and status in {
                "UNKNOWN", "REVIEW"
            }:
                print(
                    f"\n[REVIEW] Authorization could not be confirmed: "
                    f"{reason}\n"
                )

    except KeyboardInterrupt:
        print("\nUSB Activity Monitor stopped.")


if __name__ == "__main__":
    try:
        main()
    except PermissionError:
        print(
            "Permission denied. Try running with sudo and the "
            "project virtual-environment Python interpreter.",
            file=sys.stderr,
        )
        sys.exit(1)
