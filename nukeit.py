#!/usr/bin/env python3
"""nukeit - network kill switch CLI"""

import sys
import os
import json
import subprocess
import ctypes
import argparse
from pathlib import Path

STATE_DIR = Path.home() / ".nukeit"
STATE_FILE = STATE_DIR / "state.json"
RULE_IN = "NUKEIT_BLOCK_IN"
RULE_OUT = "NUKEIT_BLOCK_OUT"


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def elevate():
    args = " ".join(f'"{a}"' for a in sys.argv)
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, args, None, 1
    )
    sys.exit(0)


def ps(command):
    return subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True,
        text=True,
    )


def get_active_adapters():
    result = ps(
        "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -ExpandProperty Name"
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    return [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]


def disable_adapters(adapters):
    for adapter in adapters:
        ps(f'Disable-NetAdapter -Name "{adapter}" -Confirm:$false')


def enable_adapters(adapters):
    for adapter in adapters:
        ps(f'Enable-NetAdapter -Name "{adapter}" -Confirm:$false')


def add_firewall_block():
    ps(f'New-NetFirewallRule -DisplayName "{RULE_IN}" -Direction Inbound -Action Block -Profile Any -Enabled True')
    ps(f'New-NetFirewallRule -DisplayName "{RULE_OUT}" -Direction Outbound -Action Block -Profile Any -Enabled True')


def remove_firewall_block():
    ps(f'Remove-NetFirewallRule -DisplayName "{RULE_IN}" -ErrorAction SilentlyContinue')
    ps(f'Remove-NetFirewallRule -DisplayName "{RULE_OUT}" -ErrorAction SilentlyContinue')


def is_nuked():
    return STATE_FILE.exists()


def nuke():
    adapters = get_active_adapters()

    if not adapters:
        print("No active adapters found.")

    STATE_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps({"adapters": adapters}, indent=2))

    print(f"[*] Disabling {len(adapters)} adapter(s): {', '.join(adapters) or 'none'}")
    disable_adapters(adapters)

    print("[*] Adding firewall block rules...")
    add_firewall_block()

    print("[!] Network killed. Run 'nukeit' again to restore.")


def restore():
    state = json.loads(STATE_FILE.read_text())
    adapters = state.get("adapters", [])

    print("[*] Removing firewall block rules...")
    remove_firewall_block()

    print(f"[*] Re-enabling {len(adapters)} adapter(s): {', '.join(adapters) or 'none'}")
    enable_adapters(adapters)

    STATE_FILE.unlink()
    print("[+] Network restored.")


def cmd_status():
    if is_nuked():
        state = json.loads(STATE_FILE.read_text())
        adapters = state.get("adapters", [])
        print("Status : NUKED")
        print(f"Adapters on hold : {', '.join(adapters) or 'none'}")
    else:
        adapters = get_active_adapters()
        print("Status : LIVE")
        print(f"Active adapters : {', '.join(adapters) or 'none'}")


def cmd_list():
    if is_nuked():
        print("Already nuked. Run 'nukeit' to restore first.")
        return
    adapters = get_active_adapters()
    if not adapters:
        print("No active adapters found.")
        return
    print("Adapters that would be killed:")
    for a in adapters:
        print(f"  - {a}")


def main():
    parser = argparse.ArgumentParser(
        prog="nukeit",
        description="Network kill switch — toggles all interfaces and firewall off/on.",
    )
    parser.add_argument("--status", action="store_true", help="Show current state")
    parser.add_argument("--list", action="store_true", help="List adapters that would be killed")
    args = parser.parse_args()

    if not is_admin():
        print("[~] Requesting admin privileges...")
        elevate()
        return

    if args.status:
        cmd_status()
    elif args.list:
        cmd_list()
    else:
        if is_nuked():
            restore()
        else:
            nuke()


if __name__ == "__main__":
    main()
