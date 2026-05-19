"""Factory for creating Qt widgets based on ATDL control types."""

from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QLineEdit, QComboBox, QCheckBox, QSpinBox,
    QDateTimeEdit, QSlider, QListWidget, QListWidgetItem, QPushButton
)
from PySide6.QtCore import Qt, QDateTime, QDate, QTime, QRegularExpression
from PySide6.QtGui import QValidator, QIntValidator, QRegularExpressionValidator
import re

from atdl_forge.core import Control, Parameter, ConstraintType


class ControlFactory:
    """Creates Qt widgets based on ATDL control specifications."""

    def create_widget(self, control: Control, parameter: Parameter) -> Optional[QWidget]:
        """Create a Qt widget for the given control and parameter."""
        control_type = control.control_type or "TextField_t"

        # Normalize control type name
        if "_t" not in control_type:
            control_type = f"{control_type}_t"

        if "TextField" in control_type:
            return self._create_text_field(parameter)
        elif "DropDownList" in control_type or "Combo" in control_type:
            return self._create_combo_box(parameter)
        elif "CheckBox" in control_type:
            return self._create_checkbox(parameter)
        elif "DateTime" in control_type or "Date" in control_type:
            return self._create_datetime(parameter)
        elif "Spinner" in control_type:
            return self._create_spinner(parameter)
        elif "Slider" in control_type:
            return self._create_slider(parameter)
        elif "MultiSelect" in control_type or "List" in control_type:
            return self._create_list_widget(parameter)
        elif "Button" in control_type:
            return self._create_button(parameter)
        else:
            # Default to text field
            return self._create_text_field(parameter)

    def _create_text_field(self, parameter: Parameter) -> QLineEdit:
        """Create a text field with optional constraints."""
        field = QLineEdit()

        # Apply length constraints
        length_constraint = self._find_constraint(parameter, ConstraintType.LENGTH)
        if length_constraint and length_constraint.max_value:
            field.setMaxLength(int(length_constraint.max_value))

        # Apply regex validator if available
        regex_constraint = self._find_constraint(parameter, ConstraintType.REGEX)
        if regex_constraint and regex_constraint.pattern:
            validator = QRegularExpressionValidator(QRegularExpression(regex_constraint.pattern))
            field.setValidator(validator)

        # Set default value if available
        if parameter.default_value:
            field.setText(parameter.default_value)

        field.setToolTip(parameter.description or "")
        return field

    def _create_combo_box(self, parameter: Parameter) -> QComboBox:
        """Create a combo box with allowed values."""
        combo = QComboBox()

        # Get allowed values from constraints
        allowed_values_constraint = self._find_constraint(parameter, ConstraintType.ALLOWED_VALUES)
        if allowed_values_constraint and allowed_values_constraint.allowed_values:
            combo.addItems(allowed_values_constraint.allowed_values)
        else:
            # Fallback: no values available
            combo.addItem("")

        # Set default if available
        if parameter.default_value and combo.findText(parameter.default_value) >= 0:
            combo.setCurrentText(parameter.default_value)

        combo.setToolTip(parameter.description or "")
        return combo

    def _create_checkbox(self, parameter: Parameter) -> QCheckBox:
        """Create a checkbox."""
        checkbox = QCheckBox()

        # Set default value
        if parameter.default_value:
            checkbox.setChecked(parameter.default_value.lower() in ["true", "yes", "y", "1"])

        checkbox.setToolTip(parameter.description or "")
        return checkbox

    def _create_datetime(self, parameter: Parameter) -> QDateTimeEdit:
        """Create a date/time picker."""
        picker = QDateTimeEdit()
        picker.setDateTime(QDateTime.currentDateTime())
        picker.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        picker.setCalendarPopup(True)

        # Set default if available (expect YYYYMMDD-HH:MM:SS format)
        if parameter.default_value:
            try:
                dt = self._parse_datetime(parameter.default_value)
                if dt:
                    picker.setDateTime(dt)
            except Exception:
                pass

        picker.setToolTip(parameter.description or "")
        return picker

    def _create_spinner(self, parameter: Parameter) -> QSpinBox:
        """Create a spinner for numeric values."""
        spinner = QSpinBox()

        # Apply integer range constraints
        int_constraint = self._find_constraint(parameter, ConstraintType.INT_RANGE)
        if int_constraint:
            if int_constraint.min_value is not None:
                spinner.setMinimum(int(int_constraint.min_value))
            if int_constraint.max_value is not None:
                spinner.setMaximum(int(int_constraint.max_value))

        # Set default
        if parameter.default_value:
            try:
                spinner.setValue(int(parameter.default_value))
            except ValueError:
                pass

        spinner.setToolTip(parameter.description or "")
        return spinner

    def _create_slider(self, parameter: Parameter) -> QSlider:
        """Create a slider for numeric values."""
        slider = QSlider(Qt.Horizontal)

        # Apply constraints
        int_constraint = self._find_constraint(parameter, ConstraintType.INT_RANGE)
        if int_constraint:
            if int_constraint.min_value is not None:
                slider.setMinimum(int(int_constraint.min_value))
            if int_constraint.max_value is not None:
                slider.setMaximum(int(int_constraint.max_value))

        # Set default
        if parameter.default_value:
            try:
                slider.setValue(int(parameter.default_value))
            except ValueError:
                pass

        slider.setToolTip(parameter.description or "")
        return slider

    def _create_list_widget(self, parameter: Parameter) -> QListWidget:
        """Create a multi-select list widget."""
        list_widget = QListWidget()

        # Get allowed values
        allowed_values_constraint = self._find_constraint(parameter, ConstraintType.ALLOWED_VALUES)
        if allowed_values_constraint and allowed_values_constraint.allowed_values:
            for value in allowed_values_constraint.allowed_values:
                item = QListWidgetItem(value)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                list_widget.addItem(item)

        list_widget.setToolTip(parameter.description or "")
        return list_widget

    def _create_button(self, parameter: Parameter) -> QPushButton:
        """Create a button."""
        button = QPushButton(parameter.label)
        button.setToolTip(parameter.description or "")
        return button

    def _find_constraint(self, parameter: Parameter, constraint_type: ConstraintType):
        """Find the first constraint of a given type."""
        for constraint in parameter.constraints:
            if constraint.type == constraint_type:
                return constraint
        return None

    def _parse_datetime(self, value: str) -> Optional[QDateTime]:
        """Parse datetime from various formats."""
        # Try YYYYMMDD-HH:MM:SS format
        try:
            parts = value.split("-")
            if len(parts) == 2:
                date_part = parts[0]
                time_part = parts[1]
                year = int(date_part[:4])
                month = int(date_part[4:6])
                day = int(date_part[6:8])
                hour, minute, second = map(int, time_part.split(":"))
                return QDateTime(QDate(year, month, day), QTime(hour, minute, second))
        except (ValueError, IndexError):
            pass

        # Try ISO format
        try:
            return QDateTime.fromString(value, Qt.ISODate)
        except Exception:
            pass

        return None
