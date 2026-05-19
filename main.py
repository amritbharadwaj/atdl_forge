#!/usr/bin/env python3
"""ATDL Forge - Main entry point."""

import sys
from PySide6.QtWidgets import QApplication
from atdl_forge.ui import MainWindow
from atdl_forge.ui.theme import load_theme


def main():
    """Run the ATDL Forge application."""
    app = QApplication(sys.argv)
    app.setStyleSheet(load_theme())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
