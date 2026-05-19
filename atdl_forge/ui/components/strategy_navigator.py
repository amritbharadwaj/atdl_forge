"""Left strategy catalog panel."""

from typing import List, Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QFrame,
)


class StrategyNavigator(QWidget):
    """Lists loaded strategies; selection drives the order ticket."""

    strategy_selected = Signal(str)

    EMPTY_MESSAGE = "Load an ATDL file to begin"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("strategyNavigatorPanel")
        self._current_name: Optional[str] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("Strategies")
        header.setObjectName("panelHeader")
        layout.addWidget(header)

        subtitle = QLabel("Algo / strategy catalog")
        subtitle.setObjectName("panelSubtitle")
        layout.addWidget(subtitle)

        frame = QFrame()
        frame.setObjectName("panelFrame")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(4, 4, 4, 4)

        self._list = QListWidget()
        self._list.setObjectName("strategyNavigator")
        self._list.currentTextChanged.connect(self._on_selection_changed)
        frame_layout.addWidget(self._list)

        self._empty_label = QLabel(self.EMPTY_MESSAGE)
        self._empty_label.setObjectName("emptyState")
        self._empty_label.setWordWrap(True)
        frame_layout.addWidget(self._empty_label)

        layout.addWidget(frame, 1)

        self._show_empty_state(True)

    def set_strategies(self, names: List[str]) -> None:
        """Populate the navigator with strategy names."""
        self._list.blockSignals(True)
        self._list.clear()
        for name in names:
            self._list.addItem(QListWidgetItem(name))
        self._list.blockSignals(False)

        has_strategies = bool(names)
        self._show_empty_state(not has_strategies)
        if has_strategies:
            self._list.setCurrentRow(0)

    def clear_strategies(self) -> None:
        """Reset to empty state."""
        self._list.blockSignals(True)
        self._list.clear()
        self._list.blockSignals(False)
        self._current_name = None
        self._show_empty_state(True)

    def select_strategy(self, name: str) -> None:
        """Select a strategy by name without emitting duplicate signals."""
        items = self._list.findItems(name, Qt.MatchExactly)
        if not items:
            return
        row = self._list.row(items[0])
        self._list.blockSignals(True)
        self._list.setCurrentRow(row)
        self._list.blockSignals(False)
        self._current_name = name

    def current_strategy_name(self) -> Optional[str]:
        item = self._list.currentItem()
        return item.text() if item else None

    def _show_empty_state(self, empty: bool) -> None:
        self._empty_label.setVisible(empty)
        self._list.setVisible(not empty)

    def _on_selection_changed(self, name: str) -> None:
        if not name:
            return
        self._current_name = name
        self.strategy_selected.emit(name)
