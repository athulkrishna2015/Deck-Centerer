# [Deck Centerer](https://github.com/athulkrishna2015/Deck-Centerer)
[Install from anki web](https://ankiweb.net/shared/info/1520580564)

Remembers the last reviewed deck and automatically scrolls to it in Anki’s Deck Browser, with an optional temporary green outline highlight for quick visual confirmation.  
This add-on pairs well with [Review Hotmouse Plus Overview](https://ankiweb.net/shared/info/1054369752).
## Features

- Remembers the current deck ID and name when entering review or overview.  
- Auto-scrolls to that deck on Deck Browser render and when the app opens.  
- Optional green outline highlight around the target row (off by default, toggleable in settings).  
- Targets the exact saved deck on current Anki builds by deck ID, then falls back to name matching for older layouts.  
- Avoids viewport jumps while you expand or collapse deck tree nodes.  
- Configurable retry interval (milliseconds) and maximum tries.  
- Sanitizes out-of-range or malformed config values instead of crashing on bad metadata.  
- Built-in Config dialog with a “Reset to defaults” button.  
- Cross-version UI compatibility (PyQt5/PyQt6-safe settings dialog handlers).

## Requirements

- Anki 2.1+ (tested on Anki 25.09.2 with Qt 6.9.2 / PyQt 6.9.1).  
- Desktop OS supported by Anki (tested on Linux; Manjaro KDE).  

## Installation

### From source (manual)

1. Open Anki → Tools → Add-ons → Open Add-ons Folder.  
2. Create a folder named `Deck-Centerer` (or your preferred folder name).  
3. Copy the add-on source files into it. If you are copying from a local checkout, skip `meta.json` so Anki creates fresh per-user metadata.  
4. Restart Anki.  

### Updating

- Replace files in the same folder, then restart Anki.  

## Usage

- Open the Deck Browser (press D) or start Anki; the deck list will auto-scroll to the last reviewed deck.  
- If no deck has been remembered yet, the add-on stays idle and does not schedule retry loops.  
- If enabled, a temporary green outline will briefly highlight the deck row. The default is off.  

## Settings

Open Anki → Tools → Add-ons → select “Deck Centerer” → Config.  

<img width="550" height="417" alt="Screenshot_20251102_194836" src="https://github.com/user-attachments/assets/e57e02f0-4906-4b7b-8e7c-7121caa9f0ea" />


Available options:
- Center on scroll (boolean): If enabled, centers the target row; otherwise scrolls it just into view.  
- Show green outline highlight (boolean, default `false`): Toggle the temporary green outline around the found row.  
- Retry interval (ms) (integer): Delay between selection attempts after render.  
- Max tries (integer): Maximum number of selection attempts.  
- Reset to defaults: Restores shipped defaults (also clears remembered last deck id/name).  

## Changelog

### 2026-03-07

#### Changed
- Prefer exact deck-ID targeting on current Anki Deck Browser markup before falling back to deck-name matching.
- Narrow the expand/collapse skip guard so normal row navigation and selection no longer suppress auto-scroll.

#### Fixed
- Fix wrong deck focusing when multiple subdecks share the same leaf name and the first matching name appeared earlier in the list.
- Stop scheduling repeated scroll retries when no deck has been remembered yet.
- Clamp and sanitize malformed config values loaded from metadata.

#### Defaults
- Change the temporary green outline highlight to be disabled by default.

### 2025-11-03 

#### Added
- Add a persistent “skip” guard that activates on deck tree expand/collapse via mouse, touch, or keyboard, preventing auto-scroll during these interactions in the Deck Browser. 
- Add a MutationObserver for aria-expanded changes to catch programmatic toggles that don’t originate from direct user clicks or key presses, ensuring no unintended scroll on child subdeck expansion/collapse. 
- Add a lightweight persistence of the skip window across re-renders using a small JS bridge and storage so the guard reliably survives Deck Browser DOM refreshes. 

#### Changed
- Change the scrolling script to early-return when the skip guard is active, short-circuiting retries to avoid any viewport jump while users are expanding or collapsing deck nodes. 
- Tighten the deck row target lookup while keeping existing id/name fallbacks, maintaining compatibility with current behavior that scrolls to the last reviewed deck when appropriate. 

#### Fixed
- Fix unintended auto-scroll that occurred after expanding or collapsing parent and child subdecks in the Deck Browser by gating the behavior behind the new skip guard and timing window. 

### 2025-10-30 
- Initial release: remember the last reviewed deck and auto-scroll to it on Deck Browser render or app start, with optional highlight and configurable timing/retry behavior. 
