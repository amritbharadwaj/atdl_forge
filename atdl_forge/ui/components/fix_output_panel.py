"""FIX message output dock panel."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit, QFrame
from PySide6.QtGui import QFont


class FixOutputPanel(QWidget):
    """Bottom dock showing generated FIX message."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("fixOutputPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QLabel("FIX Message")
        header.setObjectName("panelHeader")
        layout.addWidget(header)

        subtitle = QLabel("Order preview — pipe-delimited tags")
        subtitle.setObjectName("panelSubtitle")
        layout.addWidget(subtitle)

        frame = QFrame()
        frame.setObjectName("panelFrame")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(6, 6, 6, 6)

        self._output = QPlainTextEdit()
        self._output.setObjectName("fixOutput")
        self._output.setReadOnly(True)
        self._output.setPlaceholderText("Generate a FIX message to preview output here...")
        self._output.setMinimumHeight(100)
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        self._output.setFont(font)
        frame_layout.addWidget(self._output)

        layout.addWidget(frame, 1)

    def set_message(self, text: str) -> None:
        self._output.setPlainText(text)

    def message(self) -> str:
        return self._output.toPlainText()

    def clear(self) -> None:
        self._output.clear()
