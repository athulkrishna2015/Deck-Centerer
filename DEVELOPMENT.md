# Deck Centerer — Developer Documentation

This repository contains the source code for the **Deck Centerer** Anki add-on.

## Project Structure

```
Deck-Centerer/
├── addon/                        # Core add-on package (this is what Anki loads)
│   ├── __init__.py               # Entry point: registers hooks
│   ├── config.py                 # Coercion and retrieval of configuration values
│   ├── constants.py              # Configuration keys and default configuration values
│   ├── decks.py                  # Core logic for scroll execution & toggle guard JS injection
│   ├── hooks.py                  # Registration of modern profile, state, and render hooks
│   ├── js.py                     # Scroll/highlight JS generator
│   ├── legacy.py                 # Compatibility helpers for older Anki versions
│   ├── settings.py               # Addon Config button handler
│   ├── config.json               # Default configuration schema
│   ├── manifest.json             # Anki package manifest (versioning and package metadata)
│   └── VERSION                   # Text file containing the raw version string (e.g. 2.2.1)
├── bump.py                       # Version auto-increment script
├── make_ankiaddon.py             # Packaging script → produces .ankiaddon file
├── README.md                     # General documentation and user-facing installation guide
└── DEVELOPMENT.md                # Developer documentation (this file)
```

---

## Development Workflow

### 1. Local Testing (Symlinking)

The fastest way to test changes is to symlink the `addon/` folder directly into your Anki add-ons directory so Anki loads your live code on every restart.

**Linux/macOS:**
```shell
ln -s "$(pwd)/addon" ~/.local/share/Anki2/addons21/deck_centerer_dev
```

**Windows (Admin PowerShell):**
```powershell
New-Item -ItemType SymbolicLink -Path "$env:APPDATA\Anki2\addons21\deck_centerer_dev" -Target "$pwd\addon"
```

---

## Building and Versioning

### Build the `.ankiaddon` package

```shell
# Auto-bump patch version and build:
python3 make_ankiaddon.py

# Set an explicit version:
python3 make_ankiaddon.py 2.2.2
```

This produces a timestamped file like `Deck_Centerer_v2.2.2_202607071200.ankiaddon`.

### Manually bump the version

```shell
python3 bump.py patch
```

Follows `major.minor.patch` semver.

---

## Code Standards

- Maintain compatibility with modern **Anki** versions (Qt 6, PyQt 6, Python 3.9+).
- Defer heavy or early execution to avoid blocking Anki startup.
