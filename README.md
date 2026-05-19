# ATDL Forge

A cross-platform desktop application for rendering FIXatdl XML files and generating FIX messages. Built with PySide6 and a light OMS/EMS-style order ticket UI.

## Features

- **ATDL parsing:** Parameters, constraints, controls, and state rules (parsed)
- **OMS-style layout:** Strategy catalog, order ticket, inspector, and FIX output dock
- **Toolbar actions:** Load, Validate, Generate FIX, Copy FIX
- **Required-field validation:** Highlights missing required parameters before FIX generation
- **8+ control types:** TextField, DropDownList, CheckBox, DateTimeEdit, Spinner, Slider, and more
- **Inspector panel:** FIX tag, constraints, and descriptions for the focused parameter

## Requirements

- Python 3.10+
- PySide6 >= 6.7.0

## Installation & Setup

```bash
git clone https://github.com/amritbharadwaj/ATDL_Forge.git
cd ATDL_Forge

pip install -r requirements.txt

# Optional: dev/build tools (PyInstaller, pytest, black, mypy)
pip install -e ".[dev]"

python main.py
```

## Usage

1. **Load ATDL XML** (toolbar or File menu) and select your FIXatdl file
2. Pick a **strategy** from the left catalog
3. Fill the **Order Parameters** ticket in the center
   - Required fields are marked with `*`
   - Click **Validate** to check required fields (invalid fields are highlighted)
4. Focus a field to see metadata in the **Inspector** (right)
5. **Generate FIX** to build the message in the bottom dock
6. **Copy FIX** to copy the message to the clipboard

## UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Menu  │  Load │ Validate │ Generate FIX │ Copy FIX          │
├──────────┬──────────────────────────────┬──────────────────┤
│ Strategies│  Order Parameters (ticket)  │  Inspector       │
│  catalog  │                              │                  │
├──────────┴──────────────────────────────┴──────────────────┤
│ FIX Message (preview dock)                                    │
├─────────────────────────────────────────────────────────────┤
│ Status: file · strategy count · validation                    │
└─────────────────────────────────────────────────────────────┘
```

## Architecture

```
atdl_forge/
├── core/
│   ├── atdl_parser.py
│   ├── models.py
│   └── fix_generator.py
└── ui/
    ├── main_window.py           # OMS shell
    ├── parameter_form.py        # Order ticket
    ├── parameter_details_panel.py
    ├── theme/
    │   └── light_oms.qss        # Light professional theme
    ├── components/
    │   ├── toolbar.py
    │   ├── strategy_navigator.py
    │   └── fix_output_panel.py
    └── widgets/
        └── control_factory.py
```

## Building Standalone Executables

```bash
pip install -e ".[dev]"
python -m PyInstaller --noconfirm --clean build.spec
# Output: dist/ATDL Forge.exe
```

Build artifacts (`dist/`, `build/`) are local only and not committed to git.

## Known Limitations

- State rules are parsed but not evaluated (no conditional visibility yet)
- Complex `StrategyPanel` hierarchies from production ATDL are not fully rendered
- Cross-parameter validation not implemented

## Planned Tools (Phase 2)

- **Strategy Visualizer:** Parameter map, layout tree, dependency graph from state rules
- **State rules engine:** Dynamic show/hide and enable/disable on the ticket
- **Preset manager:** Save and load ticket field values
- **Enum / ValidValues browser** for production algo definitions

## Author

Amrit Bharadwaj

## Version

1.1.0 — OMS UI Phase 1 (2025)
