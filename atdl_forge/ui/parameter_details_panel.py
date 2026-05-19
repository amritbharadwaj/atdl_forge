"""Parameter details panel showing constraints and metadata."""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
)
from PySide6.QtGui import QFont

from atdl_forge.core import Strategy, Parameter, ConstraintType


class ParameterDetailsPanel(QWidget):
    """Inspector panel for the selected parameter."""

    def __init__(self):
        super().__init__()
        self.setObjectName("inspectorPanel")
        self.current_strategy: Optional[Strategy] = None
        self.current_parameter: Optional[Parameter] = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QLabel("Inspector")
        header.setObjectName("panelHeader")
        main_layout.addWidget(header)

        subtitle = QLabel("Parameter metadata and constraints")
        subtitle.setObjectName("panelSubtitle")
        main_layout.addWidget(subtitle)

        frame = QFrame()
        frame.setObjectName("panelFrame")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(6, 6, 6, 6)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout()
        self.details_layout.setContentsMargins(4, 4, 4, 4)
        self.details_widget.setLayout(self.details_layout)
        self.scroll_area.setWidget(self.details_widget)
        frame_layout.addWidget(self.scroll_area)

        main_layout.addWidget(frame, 1)

        self.title = QLabel("Select a parameter to view details")
        self.title.setObjectName("panelHeader")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.title.setFont(font)
        self.details_layout.addWidget(self.title)

    def clear(self):
        self.current_parameter = None
        self.title.setText("Select a parameter to view details")

        while self.details_layout.count() > 1:
            item = self.details_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

    def on_parameter_focused(self, param_ref: str):
        if not self.current_strategy:
            return
        param = self.current_strategy.get_parameter_by_ref(param_ref)
        if param:
            self._display_parameter_details(param)

    def _display_parameter_details(self, parameter: Parameter):
        self.current_parameter = parameter
        self.clear()

        self.title.setText(parameter.label or parameter.name)

        self._add_detail_row("Name:", parameter.name)
        self._add_detail_row("FIX Tag:", parameter.fix_tag)

        if parameter.required:
            label = QLabel("Required: Yes")
            label.setObjectName("detailRequired")
            self.details_layout.addWidget(label)
        else:
            self._add_detail_row("Required:", "No")

        if parameter.param_type:
            self._add_detail_row("Type:", parameter.param_type)

        if parameter.constraints:
            self.details_layout.addSpacing(8)
            constraints_title = QLabel("Constraints")
            constraints_title.setObjectName("detailLabel")
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
                        label.setObjectName("detailLabel")
                        self.details_layout.addWidget(label)
                        values_label = QLabel(values_text)
                        values_label.setObjectName("detailAllowedValues")
                        values_label.setWordWrap(True)
                        self.details_layout.addWidget(values_label)

        if parameter.description:
            self.details_layout.addSpacing(8)
            desc_title = QLabel("Description")
            desc_title.setObjectName("detailLabel")
            font = QFont()
            font.setBold(True)
            desc_title.setFont(font)
            self.details_layout.addWidget(desc_title)

            desc_label = QLabel(parameter.description)
            desc_label.setObjectName("detailValue")
            desc_label.setWordWrap(True)
            self.details_layout.addWidget(desc_label)

        self.details_layout.addStretch()

    def _add_detail_row(self, label_text: str, value_text: str):
        label = QLabel(label_text)
        label.setObjectName("detailLabel")
        self.details_layout.addWidget(label)

        value = QLabel(value_text)
        value.setObjectName("detailValue")
        value.setWordWrap(True)
        self.details_layout.addWidget(value)
        self.details_layout.addSpacing(4)
