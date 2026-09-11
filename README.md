# YARI PBQ Sims

Desktop performance-based-question (PBQ) simulators for CompTIA exam prep, built with PySide6.
Each exam is its own self-contained app, packaged independently as a Windows `.exe` with PyInstaller.

Originally prototyped as standalone HTML pages (kept for reference in `legacy-html/`), now
ported to native desktop apps with progress saved locally to `~/.yari_pbq/<app>.json`.

## Apps

| App | Exam | Question types |
|---|---|---|
| [`projectplus/`](projectplus) | Project+ | Sequencing, Matching, Calculation, Classification |
| [`aplus/`](aplus) | A+ Core 1 & 2 | Fill-in (subnetting), Matching, Sequencing, Scenario |
| [`netplus/`](netplus) | Network+ | Sequencing, Matching, Calculation, Classification, **Topology Builder**, **CLI Terminal Sim** |
| [`secplus/`](secplus) | Security+ | Sequencing, Matching, Calculation, Classification, **Log Triage**, **Firewall/ACL Builder**, **Linux Terminal Sim** |

## Setup (shared dev environment)

All four apps share one virtual environment for development:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run an app

```
venv\Scripts\activate
cd projectplus   # or aplus / netplus / secplus
python main.py
```

## Build a Windows .exe

Each app builds independently, from its own folder:

```
venv\Scripts\activate
cd netplus
pyinstaller --noconsole --onefile --name YARI-NetworkPlus-PBQ main.py
```

The finished executable lands in `netplus/dist/YARI-NetworkPlus-PBQ.exe`. Repeat per app,
swapping the `--name` and directory.
