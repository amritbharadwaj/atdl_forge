"""Application toolbar with OMS-style actions."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QToolBar, QWidget
from PySide6.QtGui import QAction


class AppToolBar(QToolBar):
    """Toolbar for primary trading-desk actions."""

    load_requested = Signal()
    validate_requested = Signal()
    generate_requested = Signal()
    copy_fix_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Main", parent)
        self.setObjectName("appToolBar")
        self.setMovable(False)
        self.setFloatable(False)

        load_action = QAction("Load ATDL", self)
        load_action.setToolTip("Load FIXatdl XML file")
        load_action.triggered.connect(self.load_requested.emit)
        self.addAction(load_action)

        self.addSeparator()

        validate_action = QAction("Validate", self)
        validate_action.setToolTip("Validate required order parameters")
        validate_action.triggered.connect(self.validate_requested.emit)
        self.addAction(validate_action)

        generate_action = QAction("Generate FIX", self)
        generate_action.setToolTip("Generate FIX message from ticket")
        generate_action.triggered.connect(self.generate_requested.emit)
        self._generate_action = generate_action
        self.addAction(generate_action)

        self.addSeparator()

        copy_action = QAction("Copy FIX", self)
        copy_action.setToolTip("Copy FIX message to clipboard")
        copy_action.triggered.connect(self.copy_fix_requested.emit)
        self.addAction(copy_action)

        self._mark_primary(generate_action)

    def _mark_primary(self, action: QAction) -> None:
        widget = self.widgetForAction(action)
        if widget:
            widget.setProperty("primary", True)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
