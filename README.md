# nukeit

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

A one-command network kill switch for Windows. Run `nukeit` to instantly disable all network adapters and block all inbound/outbound traffic via the Windows Firewall. Run it again to restore everything exactly as it was.

---

## What it does

```
$ nukeit

[*] Disabling 2 adapter(s): Wi-Fi, Ethernet
[*] Adding firewall block rules...
[!] Network killed. Run 'nukeit' again to restore.
```

```
$ nukeit

[*] Removing firewall block rules...
[*] Re-enabling 2 adapter(s): Wi-Fi, Ethernet
[+] Network restored.
```

One toggle. No config. No leftover rules.

---

## Features

- **Toggle on/off** — remembers exactly which adapters were active and restores only those
- **Auto-elevation** — triggers a UAC prompt automatically if not running as administrator
- **Firewall rules** — adds blanket block rules for all inbound and outbound traffic
- **State persistence** — saves state to `~/.nukeit/state.json` so it survives reboots
- **Zero dependencies** — pure Python stdlib, no pip packages required

---

## Install

```bash
git clone https://github.com/yourusername/nukeit.git
cd nukeit
pip install -e .
```

After that, `nukeit` is available system-wide from any terminal.

> Requires Windows 10/11 with PowerShell available.

---

## Usage

| Command | Description |
|---|---|
| `nukeit` | Kill network (or restore if already nuked) |
| `nukeit --status` | Show current state and which adapters are affected |
| `nukeit --list` | Preview adapters that would be disabled |

---

## How it works

1. Queries active network adapters via PowerShell `Get-NetAdapter`
2. Saves their names to `~/.nukeit/state.json`
3. Disables every adapter with `Disable-NetAdapter`
4. Creates two Windows Firewall rules blocking **all** inbound and outbound traffic
5. On restore: removes the firewall rules and re-enables only the adapters that were originally active

State is written before any changes are made, so a crash or power loss mid-nuke won't leave you without a recovery path — just run `nukeit` again.

---

## Use cases

- Cut network access instantly when stepping away
- Kill internet before running untrusted executables
- Quick "go dark" toggle during sensitive work
- Test offline behaviour of apps without pulling a cable

---

## Warning

This will disconnect you from the internet, VPNs, local network shares, and any active SSH or RDP sessions. Make sure you can still access what you need locally before running.

---

## License

MIT
