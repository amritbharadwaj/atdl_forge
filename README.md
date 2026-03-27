# ATDL Forge

A small Tkinter GUI that loads FIXatdl XML, lets you pick a strategy, fills in parameters, and generates a FIX message.

## Requirements

- Python 3.x (tested with local install)
- Tkinter (bundled with standard Python on Windows)

## Run

```powershell
python .\ATDL_Forge.py
```

## Usage

1. Click **Load ATDL XML** and select your FIXatdl XML file.
2. Choose a strategy from the **Strategies** dropdown.
3. Fill out the fields generated from the strategy layout.
   - Date/time fields open a picker and are filled as `YYYYMMDD-HH:MM:SS`.
4. Click **Generate FIX Message** to see the output.

## Notes

- The UI is rendered from `<lay:Control>` elements in the FIXatdl Layout namespace.
- FIX tags in the output come from each `<Parameter>` element’s `fixTag` (or `tag`) attribute; if missing, the parameter name is used.
- The window icon is loaded from `app_icon.png` if present in the project root.

## Files

- `ATDL_Forge.py`: Main application
- `app_icon.png`: Custom app icon (optional)

## Author

Amrit Bharadwaj
