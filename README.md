# ATDL Forge MVP

A professional cross-platform desktop application for rendering FIXatdl XML files and generating FIX messages. Built with PySide6 for native Windows/Mac/Linux support.

## Features

- **Full ATDL Support:** Extracts and displays all parameter constraints (ranges, allowed values, patterns, lengths, etc.)
- **8+ Control Types:** TextField, DropDownList, CheckBox, DateTimeEdit, Spinner, Slider, MultiSelect List, and more
- **Parameter Details Panel:** View constraints, validation rules, and help text for each parameter
- **Real-time Validation:** Input validation with visual feedback (red highlights on errors)
- **Professional UI:** Split-panel layout with native widgets on Windows/Mac/Linux
- **FIX Message Generation:** Automatically generates properly formatted FIX messages

## Requirements

- Python 3.10+
- PySide6 >= 6.7.0

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/amritbharadwaj/ATDL_Forge.git
cd ATDL_Forge

# Install runtime dependencies
pip install -r requirements.txt

# Optional: dev/build tools (PyInstaller, pytest, black, mypy)
pip install -e ".[dev]"

# Run the application
python main.py
```

## Usage

1. Click **Load ATDL XML** to select your FIXatdl XML file
2. Choose a strategy from the dropdown menu
3. Fill out the parameter form on the left
   - Required parameters are marked with `*`
   - Focus on any parameter to view its constraints in the right panel
   - Validation feedback appears on invalid input
4. Click **Generate FIX Message** to create your FIX order
5. Copy the generated message from the output panel

## Architecture

```
atdl_forge/
├── core/
│   ├── atdl_parser.py       # Enhanced XML parsing with constraint extraction
│   ├── models.py             # Dataclass models (Strategy, Parameter, Control, Constraint)
│   └── fix_generator.py      # FIX message generation
├── ui/
│   ├── main_window.py        # Main PySide6 application window
│   ├── parameter_form.py     # Dynamic form rendering
│   ├── parameter_details_panel.py  # Constraint display panel
│   └── widgets/
│       └── control_factory.py # Widget factory for ATDL control types
```

## What’s Extracted from ATDL

- Parameter metadata: name, FIX tag, label, description, required flag
- Constraints: length, integer range, numeric range, regex pattern, allowed values
- Controls: widget type, position, visibility, help text
- State rules: parsed for future dependency visualization

## Building Standalone Executables

```bash
# Install PyInstaller
pip install PyInstaller

# Build for Windows/Mac/Linux using the checked-in spec
python -m PyInstaller --noconfirm --clean build.spec

# Executable location: dist/ATDL Forge.exe
```

## Known Limitations (MVP)

- State rules are parsed but not evaluated (no conditional visibility/enabling yet)
- Cross-parameter validation not implemented
- Multi-language support not available

## Future Enhancements

- State rules evaluation for dynamic field visibility/dependencies
- Advanced validation rules and cross-field validation
- Save/load parameter presets
- Dark mode and theme switching
- REST API integration for order submission

## Author

Amrit Bharadwaj

## Version

1.0.0-MVP (2025)
