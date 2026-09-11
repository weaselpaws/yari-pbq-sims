# Yari PBQ Sims

Desktop GUI app built with PySide6, packaged as a Windows .exe with PyInstaller.

## Setup

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```
python main.py
```

## Build .exe

```
pyinstaller --noconsole --onefile main.py
```
