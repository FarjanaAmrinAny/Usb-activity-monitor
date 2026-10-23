import json
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "logs" / "usb_events.jsonl"


def main():
    if not LOG_FILE.exists():
        print("No USB event log found yet.")
        print("Connect a USB device to the Kali VM and test again.")
        return

    events = []
    invalid_lines = 0

    with LOG_FILE.open(encoding="utf-8") as file:
        for line in file:
            try:
                event = json.loads(line)
                if isinstance(event, dict):
                    events.append(event)
                else:
                    invalid_lines += 1
            except json.JSONDecodeError:
                invalid_lines += 1

    print("USB ACTIVITY REPORT")
    print("=" * 30)
    print(f"Total events: {len(events)}")
    print(f"Invalid log lines: {invalid_lines}")

    actions = Counter(
        event.get("action", "unknown") for event in events
    )
    statuses = Counter(
        event.get("authorization_status", "unknown")
        for event in events
    )

    print(f"USB insertions: {actions.get('add', 0)}")
    print(f"USB removals: {actions.get('remove', 0)}")

    print("\nAuthorization summary:")
    for status, count in sorted(statuses.items()):
        print(f"{status}: {count}")

    print("\nRecent events:")
    for event in events[-10:]:
        print(
            event.get("timestamp"),
            event.get("action"),
            event.get("product"),
            event.get("authorization_status"),
        )


if __name__ == "__main__":
    main()
