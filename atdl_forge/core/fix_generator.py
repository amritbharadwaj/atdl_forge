"""FIX message generation from strategy data."""

from typing import Dict, Any
from .models import Strategy, Parameter


class FIXGenerator:
    """Generates FIX messages from strategy data."""

    def generate_message(self, strategy: Strategy, field_values: Dict[str, str]) -> str:
        """Generate a FIX message from strategy parameters and user values."""
        # Start with standard header
        fix_msg = "35=D|"
        added = set()

        # Add user-provided values
        for param_name, value in field_values.items():
            if not value:
                continue

            param = strategy.get_parameter_by_ref(param_name)
            if not param:
                continue

            fix_tag = param.fix_tag
            fix_msg += f"{fix_tag}={value}|"
            added.add(param_name)

        # Add constant values for parameters not provided
        for param_name, param in strategy.parameters.items():
            if param_name in added:
                continue
            if param.const_value:
                fix_msg += f"{param.fix_tag}={param.const_value}|"

        return fix_msg

    def generate_message_dict(self, strategy: Strategy, field_values: Dict[str, str]) -> Dict[str, str]:
        """Generate a dict of FIX tags and values."""
        result = {"35": "D"}  # Add message type

        # Add user-provided values
        for param_name, value in field_values.items():
            if not value:
                continue

            param = strategy.get_parameter_by_ref(param_name)
            if param:
                result[param.fix_tag] = value

        # Add constant values for parameters not provided
        for param_name, param in strategy.parameters.items():
            if param_name not in field_values and param.const_value:
                result[param.fix_tag] = param.const_value

        return result
