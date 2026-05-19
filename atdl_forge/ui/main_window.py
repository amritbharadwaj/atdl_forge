"""Main application window."""

import os
from typing import Optional, Dict

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFileDialog, QSplitter, QMessageBox,
    QApplication, QLabel,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction

from atdl_forge.core import ATDLParser, Strategy, FIXGenerator
from .parameter_form import ParameterForm
from .parameter_details_panel import ParameterDetailsPanel
from .components import AppToolBar, StrategyNavigator, FixOutputPanel


class MainWindow(QMainWindow):
    """Main application window for ATDL Forge."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATDL Forge")
        self.setGeometry(100, 100, 1280, 820)
        self.setMinimumSize(QSize(1100, 720))

        self.parser = ATDLParser()
        self.fix_generator = FIXGenerator()

        self.current_strategies: Dict[str, Strategy] = {}
        self.current_strategy: Optional[Strategy] = None
        self._loaded_file_path: Optional[str] = None

        self._setup_ui()
        self._set_icon()
        self._create_menu_bar()
        self._update_status("Ready")

    def _setup_ui(self):
        self._toolbar = AppToolBar(self)
        self.addToolBar(self._toolbar)

        central = QWidget()
        central.setObjectName("centralRoot")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(8)

        body_splitter = QSplitter(Qt.Horizontal)

        self.strategy_nav = StrategyNavigator()
        self.strategy_nav.setMinimumWidth(200)
        self.strategy_nav.setMaximumWidth(280)
        body_splitter.addWidget(self.strategy_nav)

        ticket_splitter = QSplitter(Qt.Horizontal)

        self.parameter_form = ParameterForm()
        ticket_splitter.addWidget(self.parameter_form)

        self.details_panel = ParameterDetailsPanel()
        self.details_panel.setMinimumWidth(260)
        ticket_splitter.addWidget(self.details_panel)

        ticket_splitter.setSizes([620, 340])
        body_splitter.addWidget(ticket_splitter)

        body_splitter.setSizes([220, 1000])
        root_layout.addWidget(body_splitter, 1)

        self.fix_panel = FixOutputPanel()
        self.fix_panel.setMaximumHeight(180)
        root_layout.addWidget(self.fix_panel)

        self.strategy_nav.strategy_selected.connect(self._on_strategy_selected)
        self.parameter_form.field_focused.connect(self.details_panel.on_parameter_focused)
        self.parameter_form.validation_changed.connect(self._on_validation_changed)

        self._toolbar.load_requested.connect(self._on_load_file)
        self._toolbar.validate_requested.connect(self._on_validate)
        self._toolbar.generate_requested.connect(self._on_generate_fix)
        self._toolbar.copy_fix_requested.connect(self._on_copy_fix)

    def _create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        load_action = QAction("Load ATDL XML", self)
        load_action.triggered.connect(self._on_load_file)
        file_menu.addAction(load_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("View")
        reset_action = QAction("Reset Layout", self)
        reset_action.setEnabled(False)
        reset_action.setToolTip("Coming in a future release")
        view_menu.addAction(reset_action)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _set_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _update_status(self, message: str) -> None:
        parts = [message]
        if self._loaded_file_path:
            parts.append(f"File: {os.path.basename(self._loaded_file_path)}")
        if self.current_strategies:
            parts.append(f"Strategies: {len(self.current_strategies)}")
        if self.current_strategy:
            parts.append(f"Active: {self.current_strategy.name}")
        self.statusBar().showMessage("  |  ".join(parts))

    def _on_load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load ATDL XML", "", "XML Files (*.xml)"
        )
        if not file_path:
            return

        try:
            self.current_strategies = self.parser.parse_file(file_path)
            self._loaded_file_path = file_path
            names = list(self.current_strategies.keys())
            self.strategy_nav.set_strategies(names)
            self.fix_panel.clear()
            self._update_status(f"Loaded {len(names)} strategy(ies)")
        except ValueError as e:
            QMessageBox.warning(self, "Load Error", str(e))
            self._update_status(f"Error: {e}")

    def _on_strategy_selected(self, strategy_name: str):
        if not strategy_name or strategy_name not in self.current_strategies:
            self.current_strategy = None
            self.details_panel.current_strategy = None
            self.parameter_form.clear()
            self.details_panel.clear()
            self._update_status("No strategy selected")
            return

        self.current_strategy = self.current_strategies[strategy_name]
        self.details_panel.current_strategy = self.current_strategy
        self.parameter_form.render_strategy(self.current_strategy)
        self.details_panel.clear()
        self._update_status(f"Strategy: {strategy_name}")

    def _on_validate(self):
        if not self.current_strategy:
            QMessageBox.information(
                self, "Validate", "Load an ATDL file and select a strategy first."
            )
            return

        is_valid, missing = self.parameter_form.validate_required()
        if is_valid:
            self._update_status("Validation passed")
            QMessageBox.information(self, "Validate", "All required parameters are filled.")
        else:
            labels = ", ".join(missing)
            self._update_status(f"Validation failed: {len(missing)} required field(s)")
            QMessageBox.warning(
                self,
                "Validation Failed",
                f"Missing required parameters:\n{labels}",
            )

    def _on_generate_fix(self):
        if not self.current_strategy:
            QMessageBox.information(
                self, "Generate FIX", "Load an ATDL file and select a strategy first."
            )
            return

        is_valid, missing = self.parameter_form.validate_required()
        if not is_valid:
            labels = ", ".join(missing)
            QMessageBox.warning(
                self,
                "Validation Failed",
                f"Fix required parameters before generating:\n{labels}",
            )
            self._update_status(f"Cannot generate: {len(missing)} required field(s) missing")
            return

        field_values = self.parameter_form.get_field_values()
        fix_msg = self.fix_generator.generate_message(self.current_strategy, field_values)
        self.fix_panel.set_message(fix_msg)
        self._update_status("FIX message generated")

    def _on_copy_fix(self):
        text = self.fix_panel.message().strip()
        if not text:
            QMessageBox.information(self, "Copy FIX", "No FIX message to copy. Generate one first.")
            return
        QApplication.clipboard().setText(text)
        self._update_status("FIX message copied to clipboard")

    def _on_validation_changed(self, is_valid: bool, error_count: int) -> None:
        if error_count > 0:
            self._update_status(f"{error_count} validation error(s)")
        elif self.current_strategy:
            self._update_status(f"Strategy: {self.current_strategy.name}")

    def _on_about(self):
        QMessageBox.about(
            self,
            "About ATDL Forge",
            "ATDL Forge\n\n"
            "FIXatdl order ticket and FIX message generator.\n"
            "Light OMS-style desk UI (Phase 1).\n\n"
            "© 2025 Amrit Bharadwaj",
        )
