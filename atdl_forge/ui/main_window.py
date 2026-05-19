"""Main application window."""

import os
from typing import Optional, Dict

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QLabel, QFileDialog, QSplitter, QTextEdit, QStatusBar,
    QMenuBar, QMenu
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction

from atdl_forge.core import ATDLParser, Strategy, FIXGenerator
from .parameter_form import ParameterForm
from .parameter_details_panel import ParameterDetailsPanel


class MainWindow(QMainWindow):
    """Main application window for ATDL Forge."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATDL Forge")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(QSize(1000, 700))

        self.parser = ATDLParser()
        self.fix_generator = FIXGenerator()

        self.current_strategies: Dict[str, Strategy] = {}
        self.current_strategy: Optional[Strategy] = None

        self._setup_ui()
        self._set_icon()
        self._create_menu_bar()

    def _setup_ui(self):
        """Set up the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Top bar: Load button and strategy selector
        top_layout = QHBoxLayout()

        load_btn = QPushButton("Load ATDL XML")
        load_btn.clicked.connect(self._on_load_file)
        top_layout.addWidget(load_btn)

        top_layout.addSpacing(20)

        strategy_label = QLabel("Strategy:")
        top_layout.addWidget(strategy_label)

        self.strategy_combo = QComboBox()
        self.strategy_combo.currentTextChanged.connect(self._on_strategy_changed)
        top_layout.addWidget(self.strategy_combo, 1)

        main_layout.addLayout(top_layout)

        # Main content: Split between form and details panel
        splitter = QSplitter(Qt.Horizontal)

        # Parameter form (left)
        self.parameter_form = ParameterForm()
        splitter.addWidget(self.parameter_form)

        # Parameter details panel (right)
        self.details_panel = ParameterDetailsPanel()
        self.parameter_form.field_focused.connect(self.details_panel.on_parameter_focused)
        splitter.addWidget(self.details_panel)

        # Set initial split ratio (70% form, 30% details)
        splitter.setSizes([840, 360])
        main_layout.addWidget(splitter)

        # Bottom: Generate FIX and output
        bottom_layout = QVBoxLayout()

        generate_btn = QPushButton("Generate FIX Message")
        generate_btn.clicked.connect(self._on_generate_fix)
        bottom_layout.addWidget(generate_btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(100)
        self.output.setPlaceholderText("FIX message will appear here...")
        bottom_layout.addWidget(self.output)

        main_layout.addLayout(bottom_layout)

        # Status bar
        self.statusBar().showMessage("Ready")

    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        load_action = QAction("Load ATDL XML", self)
        load_action.triggered.connect(self._on_load_file)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _set_icon(self):
        """Set the window icon if available."""
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _on_load_file(self):
        """Handle loading an ATDL XML file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load ATDL XML", "", "XML Files (*.xml)"
        )
        if not file_path:
            return

        try:
            self.current_strategies = self.parser.parse_file(file_path)
            self._update_strategy_selector()
            self.statusBar().showMessage(f"Loaded {len(self.current_strategies)} strategy(ies)")
        except ValueError as e:
            self.statusBar().showMessage(f"Error: {str(e)}")

    def _update_strategy_selector(self):
        """Update the strategy dropdown with loaded strategies."""
        self.strategy_combo.clear()
        if self.current_strategies:
            self.strategy_combo.addItems(list(self.current_strategies.keys()))
            self.strategy_combo.setEnabled(True)
        else:
            self.strategy_combo.setEnabled(False)

    def _on_strategy_changed(self, strategy_name: str):
        """Handle strategy selection change."""
        if not strategy_name or strategy_name not in self.current_strategies:
            self.current_strategy = None
            self.details_panel.current_strategy = None
            self.parameter_form.clear()
            self.details_panel.clear()
            return

        self.current_strategy = self.current_strategies[strategy_name]
        self.details_panel.current_strategy = self.current_strategy
        self.parameter_form.render_strategy(self.current_strategy)
        self.details_panel.clear()
        self.statusBar().showMessage(f"Strategy: {strategy_name}")

    def _on_generate_fix(self):
        """Handle FIX message generation."""
        if not self.current_strategy:
            self.statusBar().showMessage("Please load an ATDL file and select a strategy")
            return

        field_values = self.parameter_form.get_field_values()
        fix_msg = self.fix_generator.generate_message(self.current_strategy, field_values)
        self.output.setText(fix_msg)
        self.statusBar().showMessage("FIX message generated")

    def _on_about(self):
        """Show about dialog."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About ATDL Forge",
            "ATDL Forge MVP\n\n"
            "A cross-platform desktop application for rendering FIXatdl XML files "
            "and generating FIX messages.\n\n"
            "© 2025 Amrit Bharadwaj"
        )
