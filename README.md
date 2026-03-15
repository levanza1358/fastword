# FastWord

FastWord is a Windows desktop text expansion tool built with Python and PyQt6. It lets you create shortcut-based rules that can inject text, paste an image, optionally press Enter, and restrict execution to specific desktop applications.

The project is designed for fast repetitive messaging, canned replies, customer support workflows, and other high-frequency desktop text automation tasks.

## Highlights

- Global text expansion engine for Windows
- Per-rule text output
- Per-rule image paste support
- Per-rule Auto Enter
- Per-rule app targeting by executable name
- Search and filter for saved rules
- Inline editor with image preview
- Activity log with copy and clear actions
- Settings page for runtime behavior
- Optional system tray integration
- Optional Windows startup integration
- Optional engine auto-start when the app opens
- Backup export and import
- Built-in License and Donate pages

## Core Features

### Rule engine

Each rule can define:

- `Trigger`: the typed shortcut that activates the rule
- `Output Text`: the text that will be inserted
- `Image Path`: an optional image file to paste
- `Rule Enabled`: whether the rule is active
- `Auto Enter`: whether the rule submits immediately after sending content
- `Target Apps`: optional comma-separated executable names such as `discord.exe, chrome.exe`

Supported behavior:

- Text only
- Image only
- Text plus image
- Global rules
- App-specific rules

Duplicate triggers are blocked when their scope overlaps.

### Desktop UI

The desktop app includes:

- `Home` page for quick actions and summary stats
- `Word Editor` page for search, filtering, editing, preview, and CRUD
- `Activity Log` page for runtime events
- `Settings` page for global configuration
- `License` page for ownership and usage terms
- `Donate` page for support links and bank transfer info

### Settings

The current settings include:

- Default Auto Enter for new rules
- Enable system tray
- Minimize to tray
- Start with Windows
- Auto start engine when app opens
- Global delay before Enter

Note:

- Closing the window exits the application
- Only minimizing can route the app to the tray when tray support is enabled

## Requirements

- Windows 10 or Windows 11
- Python 3.12 or newer

## Installation

Install runtime dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install packaging dependencies:

```powershell
python -m pip install -r requirements-dev.txt
```

## Run From Source

```powershell
python main.py
```

## Build The Executable

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

The packaged executable is created at:

`dist\FastWord.exe`

## How FastWord Works

1. Launch the application.
2. Create one or more rules in `Word Editor`.
3. Start the engine.
4. Type a trigger in a supported target application.
5. FastWord replaces the trigger with the configured output.
6. If the rule includes an image, FastWord pastes it.
7. If Auto Enter is enabled, FastWord submits the content after the configured delay.

## Rule Targeting

`Target Apps` accepts executable names only.

Examples:

- `discord.exe`
- `chrome.exe`
- `whatsapp.exe`
- `discord.exe, chrome.exe`

Behavior:

- If `Target Apps` is empty, the rule is global
- If `Target Apps` is filled, the rule only works in those applications

## Storage

Application data is stored in:

`%APPDATA%\FastWord\rules.json`

Backups created from the app are stored in the same folder.

Legacy data from the previous app name is migrated automatically to the `FastWord` folder when available.

## Backup And Restore

FastWord supports:

- Export backup
- Import backup
- Automatic pre-import backup creation

This makes it easier to move rules between machines or restore an earlier configuration.

## Notes And Limitations

- FastWord is Windows-only.
- Some target applications handle clipboard and Enter submission differently.
- Image paste support depends on the target application accepting pasted image content.
- Auto Enter timing may need adjustment depending on the target app and the content being sent.
- For app targeting, always use executable names, not window titles.

## Donation

The desktop app includes a `Donate` page with:

- PayPal link
- Bank transfer details
- Developer GitHub link

Current bank transfer details in the app:

- Bank: `BCA`
- Account Number: `1710873620`
- Account Name: `Rizqi Ismanda Nugraha`

## License

This project is distributed under the proprietary license in [LICENSE](LICENSE).

## Developer

- Developer: `Rizqi Ismanda Nugraha`
- GitHub: `https://github.com/levanza1358`
