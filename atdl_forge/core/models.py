"""Data models for ATDL parsing and rendering."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from enum import Enum


class ConstraintType(Enum):
    """Types of constraints that can be applied to parameters."""
    LENGTH = "Length"
    INT_RANGE = "IntRange"
    NUM_RANGE = "NumRange"
    REGEX = "Regex"
    ALLOWED_VALUES = "AllowedValues"


@dataclass
class Constraint:
    """Represents a constraint on a parameter value."""
    type: ConstraintType
    min_value: Optional[int | float] = None
    max_value: Optional[int | float] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    description: Optional[str] = None


@dataclass
class Parameter:
    """Represents a parameter in a strategy."""
    name: str
    fix_tag: str
    label: str
    description: Optional[str] = None
    required: bool = False
    const_value: Optional[str] = None
    default_value: Optional[str] = None
    constraints: List[Constraint] = field(default_factory=list)
    param_type: str = "String"  # String, Integer, Float, Boolean, DateTime
    # enum_id -> wire_value (FIX value) from <EnumPair>
    enum_pairs: Dict[str, str] = field(default_factory=dict)


@dataclass
class Control:
    """Represents a UI control for a parameter."""
    parameter_ref: str
    control_type: str  # TextField_t, DropDownList_t, CheckBox_t, DateTime_t, etc.
    label: str
    position: Tuple[int, int]  # (row, column)
    help_text: Optional[str] = None
    enabled: bool = True
    visible: bool = True
    # (enum_id, ui_rep) from <ListItem> children
    list_items: List[Tuple[str, str]] = field(default_factory=list)
    init_value: Optional[str] = None


@dataclass
class Strategy:
    """Represents a trading strategy with parameters and controls."""
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    parameters: Dict[str, Parameter] = field(default_factory=dict)
    controls: List[Control] = field(default_factory=list)
    state_rules: List[Dict] = field(default_factory=list)

    def get_required_parameters(self) -> List[Parameter]:
        """Get all required parameters in this strategy."""
        return [p for p in self.parameters.values() if p.required]

    def get_parameter_by_ref(self, ref: str) -> Optional[Parameter]:
        """Get a parameter by its reference name."""
        return self.parameters.get(ref)
