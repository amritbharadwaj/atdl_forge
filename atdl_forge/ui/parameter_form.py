"""Parameter form widget for rendering strategy controls."""

from typing import Dict, List, Optional, Tuple
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QComboBox,
    QCheckBox, QScrollArea, QSpinBox, QDateTimeEdit, QSlider,
    QGroupBox,
)
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QFont

from atdl_forge.core import Strategy, Parameter
from .widgets.control_factory import ControlFactory


class ParameterForm(QWidget):
    """Widget that dynamically renders form fields from a strategy."""

    field_focused = Signal(str)
    validation_changed = Signal(bool, int)  # is_valid, error_count

    def __init__(self):
        super().__init__()
        self.setObjectName("orderTicket")
        self.current_strategy: Optional[Strategy] = None
        self.fields: Dict[str, QWidget] = {}
        self._field_params: Dict[str, Parameter] = {}
        self.control_factory = ControlFactory()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self._group = QGroupBox("Order Parameters")
        group_layout = QVBoxLayout(self._group)

        self._empty_label = QLabel("Select a strategy from the catalog to configure the order ticket.")
        self._empty_label.setObjectName("emptyState")
        self._empty_label.setWordWrap(True)
        group_layout.addWidget(self._empty_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.form_widget = QWidget()
        self.form_layout = QGridLayout()
        self.form_layout.setSpacing(10)
        self.form_layout.setContentsMargins(4, 4, 4, 4)
        self.form_widget.setLayout(self.form_layout)
        self.scroll_area.setWidget(self.form_widget)
        group_layout.addWidget(self.scroll_area)

        self._empty_label.setVisible(True)
        self.scroll_area.setVisible(False)

        main_layout.addWidget(self._group)

    def clear(self):
        """Clear all fields."""
        self.current_strategy = None
        self.fields.clear()
        self._field_params.clear()

        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._empty_label.setVisible(True)
        self.scroll_area.setVisible(False)

    def render_strategy(self, strategy: Strategy):
        """Render form fields from a strategy."""
        self.clear()
        self.current_strategy = strategy
        self._empty_label.setVisible(False)
        self.scroll_area.setVisible(True)

        controls = sorted(strategy.controls, key=lambda c: (c.position[0], c.position[1]))

        for control in controls:
            if not control.visible:
                continue

            param = strategy.get_parameter_by_ref(control.parameter_ref)
            if not param:
                continue

            label_text = control.label
            if param.required:
                label_text += " *"

            label = QLabel(label_text)
            label.setObjectName("fieldLabelRequired" if param.required else "")
            if param.required:
                font = QFont()
                font.setBold(True)
                label.setFont(font)

            row, col = control.position

            widget = self.control_factory.create_widget(control, param)
            if widget:
                widget.setProperty("invalid", False)
                widget.installEventFilter(self)
                self.fields[control.parameter_ref] = widget
                self._field_params[control.parameter_ref] = param
                widget._param_ref = control.parameter_ref

                self.form_layout.addWidget(label, row, col, 1, 1)
                self.form_layout.addWidget(widget, row, col + 1, 1, 1)

                constraint_hint = self._get_constraint_hint(param)
                if constraint_hint:
                    hint_label = QLabel(constraint_hint)
                    hint_label.setObjectName("constraintHint")
                    self.form_layout.addWidget(hint_label, row + 1, col + 1, 1, 1)

        self.clear_validation_state()

    def _get_constraint_hint(self, param: Parameter) -> Optional[str]:
        if not param.constraints:
            return None
        hints = [c.description for c in param.constraints if c.description]
        return " | ".join(hints) if hints else None

    def get_field_values(self) -> Dict[str, str]:
        values = {}
        for param_ref, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                values[param_ref] = widget.text()
            elif isinstance(widget, QComboBox):
                data = widget.currentData()
                if data is not None and data != "":
                    values[param_ref] = str(data)
                else:
                    values[param_ref] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                values[param_ref] = "Y" if widget.isChecked() else "N"
            elif isinstance(widget, QSpinBox):
                values[param_ref] = str(widget.value())
            elif isinstance(widget, QDateTimeEdit):
                dt = widget.dateTime()
                values[param_ref] = dt.toString("yyyyMMdd-HH:mm:ss")
            elif isinstance(widget, QSlider):
                values[param_ref] = str(widget.value())
        return values

    def validate_required(self) -> Tuple[bool, List[str]]:
        """Validate required fields; mark invalid widgets. Returns (ok, missing_labels)."""
        if not self.current_strategy:
            return False, []

        missing: List[str] = []
        values = self.get_field_values()

        for param_ref, param in self._field_params.items():
            widget = self.fields.get(param_ref)
            if not widget or not param.required:
                if widget:
                    self._set_invalid(widget, False)
                continue

            value = values.get(param_ref, "").strip()
            is_empty = not value or value in ("N",)
            if isinstance(widget, QCheckBox):
                is_empty = False

            if is_empty:
                missing.append(param.label or param.name)
                self._set_invalid(widget, True)
            else:
                self._set_invalid(widget, False)

        is_valid = len(missing) == 0
        self.validation_changed.emit(is_valid, len(missing))
        return is_valid, missing

    def clear_validation_state(self) -> None:
        for widget in self.fields.values():
            self._set_invalid(widget, False)
        self.validation_changed.emit(True, 0)

    def _set_invalid(self, widget: QWidget, invalid: bool) -> None:
        widget.setProperty("invalid", invalid)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            param_ref = getattr(obj, "_param_ref", None)
            if param_ref:
                self.field_focused.emit(param_ref)
                if hasattr(obj, "property") and obj.property("invalid"):
                    self._set_invalid(obj, False)
        return super().eventFilter(obj, event)
