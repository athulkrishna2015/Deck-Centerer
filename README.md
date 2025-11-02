# Deck Centerer

Remembers the last reviewed deck and automatically scrolls to it in Anki’s Deck Browser, with an optional temporary green outline highlight for quick visual confirmation.  
Repository: https://github.com/athulkrishna2015/Deck-Centerer

## Features

- Remembers current deck id and name when entering review or overview.  
- Auto-scrolls to that deck on Deck Browser render and when the app opens.  
- Optional green outline highlight around the target row (toggleable in settings).  
- Robust across Anki versions/themes: tries multiple id-based selectors, then falls back to name match.  
- Configurable retry interval (milliseconds) and maximum tries.  
- Built-in Config dialog with a “Reset to defaults” button.  
- Cross-version UI compatibility (PyQt5/PyQt6-safe settings dialog handlers).

## Requirements

- Anki 2.1+ (tested on Anki 25.09.2 with Qt 6.9.2 / PyQt 6.9.1).  
- Desktop OS supported by Anki (tested on Linux; Manjaro KDE).  

## Installation

### From source (manual)

1. Open Anki → Tools → Add-ons → Open Add-ons Folder.  
2. Create a folder named `Deck-Centerer` (or your preferred folder name).  
3. Copy these files into it:
   - `__init__.py`
   - `constants.py`
   - `config.py`
   - `js.py`
   - `decks.py`
   - `hooks.py`
   - `legacy.py`
   - `settings.py`
   - `config.json`
4. Restart Anki.  

### Updating

- Replace files in the same folder, then restart Anki.  

## Usage

- Open the Deck Browser (press D) or start Anki; the deck list will auto-scroll to the last reviewed deck.  
- If enabled, a temporary green outline will briefly highlight the deck row.  

## Settings

Open Anki → Tools → Add-ons → select “Deck Centerer” → Config.  

Available options:
- Center on scroll (boolean): If enabled, centers the target row; otherwise scrolls it just into view.  
- Show green outline highlight (boolean): Toggle the temporary green outline around the found row.  
- Retry interval (ms) (integer): Delay between selection attempts after render.  
- Max tries (integer): Maximum number of selection attempts.  
- Reset to defaults: Restores shipped defaults (also clears remembered last deck id/name).  

## Configuration (config.json)

Deck Centerer ships with these defaults; the settings dialog reads/writes the same values:

