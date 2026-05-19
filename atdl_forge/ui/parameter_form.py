"""Parameter form widget for rendering strategy controls."""

from typing import Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QComboBox,
    QCheckBox, QScrollArea, QSpinBox, QDateTimeEdit, QSlider, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from atdl_forge.core import Strategy, Control, ConstraintType
from .widgets.control_factory import ControlFactory


class ParameterForm(QWidget):
    """Widget that dynamically renders form fields from a strategy."""

    field_focused = Signal(str)  # Emitted when a field gets focus

    def __init__(self):
        super().__init__()
        self.current_strategy: Optional[Strategy] = None
        self.fields: Dict[str, QWidget] = {}
        self.control_factory = ControlFactory()

        # Main layout with scroll area
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.form_widget = QWidget()
        self.form_layout = QGridLayout()
        self.form_layout.setSpacing(8)
        self.form_layout.setContentsMargins(8, 8, 8, 8)

        self.form_widget.setLayout(self.form_layout)
        self.scroll_area.setWidget(self.form_widget)
        main_layout.addWidget(self.scroll_area)

    def clear(self):
        """Clear all fields."""
        self.current_strategy = None
        self.fields.clear()

        # Clear layout
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def render_strategy(self, strategy: Strategy):
        """Render form fields from a strategy."""
        self.clear()
        self.current_strategy = strategy

        # Sort controls by position
        controls = sorted(strategy.controls, key=lambda c: (c.position[0], c.position[1]))

        for control in controls:
            if not control.visible:
                continue

            param = strategy.get_parameter_by_ref(control.parameter_ref)
            if not param:
                continue

            # Create label
            label_text = control.label
            if param.required:
                label_text += " *"

            label = QLabel(label_text)
            if param.required:
                font = QFont()
                font.setBold(True)
                label.setFont(font)

            row, col = control.position

            # Create widget
            widget = self.control_factory.create_widget(control, param)
            if widget:
                widget.installEventFilter(self)
                self.fields[control.parameter_ref] = widget

                # Store param ref for event filter
                widget._param_ref = control.parameter_ref

                self.form_layout.addWidget(label, row, col, 1, 1)
                self.form_layout.addWidget(widget, row, col + 1, 1, 1)

                # Add constraint hint below if applicable
                constraint_hint = self._get_constraint_hint(param)
                if constraint_hint:
                    hint_label = QLabel(constraint_hint)
                    hint_label.setStyleSheet("color: gray; font-size: 10px;")
                    self.form_layout.addWidget(hint_label, row + 1, col + 1, 1, 1)

    def _get_constraint_hint(self, param) -> Optional[str]:
        """Get a text hint for parameter constraints."""
        if not param.constraints:
            return None

        hints = []
        for constraint in param.constraints:
            if constraint.description:
                hints.append(constraint.description)

        return " | ".join(hints) if hints else None

    def get_field_values(self) -> Dict[str, str]:
        """Get current values from all fields."""
        values = {}

        for param_ref, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                values[param_ref] = widget.text()
            elif isinstance(widget, QComboBox):
                values[param_ref] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                values[param_ref] = "Y" if widget.isChecked() else "N"
            elif isinstance(widget, QSpinBox):
                values[param_ref] = str(widget.value())
            elif isinstance(widget, QDateTimeEdit):
                dt = widget.dateTime()
                # Format as YYYYMMDD-HH:MM:SS (FIX UTCDateTime format)
                values[param_ref] = dt.toString("yyyyMMdd-HH:mm:ss")
            elif isinstance(widget, QSlider):
                values[param_ref] = str(widget.value())

        return values

    def eventFilter(self, obj, event):
        """Emit signal when a field gains focus."""
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.FocusIn:
            param_ref = getattr(obj, "_param_ref", None)
            if param_ref:
                self.field_focused.emit(param_ref)
        return super().eventFilter(obj, event)
