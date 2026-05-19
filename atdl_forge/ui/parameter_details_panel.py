"""Parameter details panel showing constraints and metadata."""

from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt

from atdl_forge.core import Strategy, Parameter, ConstraintType


class ParameterDetailsPanel(QWidget):
    """Panel showing detailed information about a selected parameter."""

    def __init__(self):
        super().__init__()
        self.current_strategy: Optional[Strategy] = None
        self.current_parameter: Optional[Parameter] = None

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Scroll area for details
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout()
        self.details_widget.setLayout(self.details_layout)
        self.scroll_area.setWidget(self.details_widget)

        main_layout.addWidget(self.scroll_area)

        # Title
        self.title = QLabel("Select a parameter to view details")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.title.setFont(font)
        self.details_layout.addWidget(self.title)

    def clear(self):
        """Clear all details."""
        self.current_parameter = None
        self.title.setText("Select a parameter to view details")

        # Clear other labels
        while self.details_layout.count() > 1:
            item = self.details_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

    def on_parameter_focused(self, param_ref: str):
        """Update details when a parameter gets focus."""
        if not self.current_strategy:
            return

        param = self.current_strategy.get_parameter_by_ref(param_ref)
        if param:
            self._display_parameter_details(param)

    def _display_parameter_details(self, parameter: Parameter):
        """Display detailed information about a parameter."""
        self.current_parameter = parameter
        self.clear()

        # Update title
        self.title.setText(parameter.label or parameter.name)

        # Basic info
        self._add_detail_row("Name:", parameter.name)
        self._add_detail_row("FIX Tag:", parameter.fix_tag)

        if parameter.required:
            label = QLabel("Required: Yes")
            label.setStyleSheet("color: red; font-weight: bold;")
            self.details_layout.addWidget(label)
        else:
            self._add_detail_row("Required:", "No")

        if parameter.param_type:
            self._add_detail_row("Type:", parameter.param_type)

        # Constraints
        if parameter.constraints:
            self.details_layout.addSpacing(12)
            constraints_title = QLabel("Constraints")
            font = QFont()
            font.setBold(True)
            constraints_title.setFont(font)
            self.details_layout.addWidget(constraints_title)

            for constraint in parameter.constraints:
                if constraint.type == ConstraintType.LENGTH:
                    min_val = constraint.min_value or "-"
                    max_val = constraint.max_value or "-"
                    self._add_detail_row("Length:", f"{min_val} to {max_val} chars")

                elif constraint.type == ConstraintType.INT_RANGE:
                    min_val = constraint.min_value or "-"
                    max_val = constraint.max_value or "-"
                    self._add_detail_row("Range:", f"{min_val} to {max_val}")

                elif constraint.type == ConstraintType.NUM_RANGE:
                    min_val = constraint.min_value or "-"
                    max_val = constraint.max_value or "-"
                    self._add_detail_row("Range:", f"{min_val} to {max_val}")

                elif constraint.type == ConstraintType.REGEX:
                    if constraint.pattern:
                        self._add_detail_row("Pattern:", constraint.pattern)

                elif constraint.type == ConstraintType.ALLOWED_VALUES:
                    if constraint.allowed_values:
                        values_text = ", ".join(constraint.allowed_values)
                        label = QLabel("Allowed Values:")
                        font = QFont()
                        font.setBold(True)
                        label.setFont(font)
                        self.details_layout.addWidget(label)

                        values_label = QLabel(values_text)
                        values_label.setWordWrap(True)
                        values_label.setStyleSheet("color: #0066cc; margin-left: 10px;")
                        self.details_layout.addWidget(values_label)

        # Description / Help
        if parameter.description:
            self.details_layout.addSpacing(12)
            desc_title = QLabel("Description")
            font = QFont()
            font.setBold(True)
            desc_title.setFont(font)
            self.details_layout.addWidget(desc_title)

            desc_label = QLabel(parameter.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #555555;")
            self.details_layout.addWidget(desc_label)

        # Spacer
        self.details_layout.addStretch()

    def _add_detail_row(self, label_text: str, value_text: str):
        """Add a label-value row to the details."""
        row_layout = QVBoxLayout()

        label = QLabel(label_text)
        font = QFont()
        font.setBold(True)
        label.setFont(font)
        row_layout.addWidget(label)

        value = QLabel(value_text)
        value.setStyleSheet("margin-left: 10px; color: #333333;")
        row_layout.addWidget(value)

        row_layout.addSpacing(4)

        # Add to main layout
        for i in range(row_layout.count()):
            widget = row_layout.itemAt(i).widget()
            if widget:
                self.details_layout.addWidget(widget)
