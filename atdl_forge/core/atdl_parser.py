"""Enhanced ATDL XML parser that extracts constraints and metadata."""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
import re

from .models import Strategy, Parameter, Control, Constraint, ConstraintType


class ATDLParser:
    """Parses FIXatdl XML files and extracts strategies with full constraint data."""

    NAMESPACES = {
        'atdl': 'http://www.fixprotocol.org/FIXatdl-1-1/Core',
        'lay': 'http://www.fixprotocol.org/FIXatdl-1-1/Layout',
        'val': 'http://www.fixprotocol.org/FIXatdl-1-1/Validation',
        'flow': 'http://www.fixprotocol.org/FIXatdl-1-1/Flow',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    }

    def parse_file(self, file_path: str) -> Dict[str, Strategy]:
        """Parse an ATDL XML file and return strategies."""
        try:
            with open(file_path, "rb") as f:
                raw = f.read()
            xml_text = raw.decode("utf-8-sig")
            root = ET.fromstring(xml_text)
        except (OSError, UnicodeDecodeError) as exc:
            raise ValueError(f"Failed to read XML file: {exc}") from exc
        except ET.ParseError as exc:
            raise ValueError(f"XML parse error: {exc}") from exc

        return self.parse_root(root)

    def parse_string(self, xml_string: str) -> Dict[str, Strategy]:
        """Parse an ATDL XML string and return strategies."""
        try:
            root = ET.fromstring(xml_string)
        except ET.ParseError as exc:
            raise ValueError(f"XML parse error: {exc}") from exc

        return self.parse_root(root)

    def parse_root(self, root: ET.Element) -> Dict[str, Strategy]:
        """Parse the root element and extract all strategies."""
        strategies = {}

        for strategy_elem in root.findall('.//atdl:Strategy', self.NAMESPACES):
            strategy = self._parse_strategy(strategy_elem)
            if strategy:
                strategies[strategy.name] = strategy

        return strategies

    def _parse_strategy(self, strategy_elem: ET.Element) -> Optional[Strategy]:
        """Parse a single strategy element."""
        name = strategy_elem.get('name')
        if not name:
            return None

        description = strategy_elem.get('description')
        version = strategy_elem.get('versionID')

        # Extract parameters
        parameters = self._extract_parameters(strategy_elem)

        # Extract controls (layout)
        controls = self._extract_controls(strategy_elem)

        # Extract state rules
        state_rules = self._extract_state_rules(strategy_elem)

        return Strategy(
            name=name,
            description=description,
            version=version,
            parameters=parameters,
            controls=controls,
            state_rules=state_rules,
        )

    def _extract_parameters(self, strategy_elem: ET.Element) -> Dict[str, Parameter]:
        """Extract all parameters from a strategy."""
        parameters = {}

        for param_elem in strategy_elem.findall('.//atdl:Parameter', self.NAMESPACES):
            param = self._parse_parameter(param_elem)
            if param:
                parameters[param.name] = param

        return parameters

    def _parse_parameter(self, param_elem: ET.Element) -> Optional[Parameter]:
        """Parse a single parameter element."""
        name = param_elem.get('name')
        if not name:
            return None

        fix_tag = param_elem.get('fixTag') or param_elem.get('tag') or name
        label = param_elem.get('label', name)
        description = param_elem.get('description')
        required = param_elem.get('required', 'false').lower() == 'true'
        const_value = param_elem.get('constValue')
        default_value = param_elem.get('defaultValue') or param_elem.get('initValue')
        param_type = param_elem.get('type') or param_elem.get('{http://www.w3.org/2001/XMLSchema-instance}type', 'String')
        if '}' in param_type:
            param_type = param_type.split(':', 1)[-1].replace('_t', '')

        enum_pairs = self._extract_enum_pairs(param_elem)

        # Extract constraints
        constraints = self._extract_constraints(param_elem)

        return Parameter(
            name=name,
            fix_tag=fix_tag,
            label=label,
            description=description,
            required=required,
            const_value=const_value,
            default_value=default_value,
            constraints=constraints,
            param_type=param_type,
            enum_pairs=enum_pairs,
        )

    def _extract_constraints(self, param_elem: ET.Element) -> List[Constraint]:
        """Extract all constraints from a parameter element."""
        constraints = []

        # Length constraint
        length_elem = param_elem.find('atdl:LengthConstraint', self.NAMESPACES)
        if length_elem is not None:
            min_len = length_elem.get('min')
            max_len = length_elem.get('max')
            constraints.append(Constraint(
                type=ConstraintType.LENGTH,
                min_value=int(min_len) if min_len else None,
                max_value=int(max_len) if max_len else None,
                description=f"Length {min_len}-{max_len}" if min_len or max_len else None,
            ))

        # Integer range constraint
        int_range_elem = param_elem.find('atdl:IntRangeConstraint', self.NAMESPACES)
        if int_range_elem is not None:
            min_val = int_range_elem.get('min')
            max_val = int_range_elem.get('max')
            constraints.append(Constraint(
                type=ConstraintType.INT_RANGE,
                min_value=int(min_val) if min_val else None,
                max_value=int(max_val) if max_val else None,
                description=f"Range {min_val}-{max_val}" if min_val or max_val else None,
            ))

        # Numeric range constraint
        num_range_elem = param_elem.find('atdl:NumRangeConstraint', self.NAMESPACES)
        if num_range_elem is not None:
            min_val = num_range_elem.get('min')
            max_val = num_range_elem.get('max')
            constraints.append(Constraint(
                type=ConstraintType.NUM_RANGE,
                min_value=float(min_val) if min_val else None,
                max_value=float(max_val) if max_val else None,
                description=f"Range {min_val}-{max_val}" if min_val or max_val else None,
            ))

        # Regex constraint
        regex_elem = param_elem.find('atdl:RegExConstraint', self.NAMESPACES)
        if regex_elem is not None:
            pattern = regex_elem.get('pattern')
            constraints.append(Constraint(
                type=ConstraintType.REGEX,
                pattern=pattern,
                description=f"Pattern: {pattern}",
            ))

        # Allowed values
        allowed_values = self._extract_allowed_values(param_elem)
        if allowed_values:
            constraints.append(Constraint(
                type=ConstraintType.ALLOWED_VALUES,
                allowed_values=allowed_values,
                description=f"Allowed: {', '.join(allowed_values)}",
            ))

        return constraints

    def _extract_allowed_values(self, param_elem: ET.Element) -> Optional[List[str]]:
        """Extract allowed values from a parameter."""
        allowed_values = []

        # Find ValidValues element
        valid_values_elem = param_elem.find('.//atdl:ValidValues', self.NAMESPACES)
        if valid_values_elem is not None:
            for value_elem in valid_values_elem.findall('atdl:ValidValue', self.NAMESPACES):
                value = value_elem.get('value')
                if value:
                    allowed_values.append(value)

        return allowed_values if allowed_values else None

    def _extract_enum_pairs(self, param_elem: ET.Element) -> Dict[str, str]:
        """Extract enumID -> wireValue mappings from a parameter."""
        pairs: Dict[str, str] = {}
        for ep in param_elem.findall('atdl:EnumPair', self.NAMESPACES) + param_elem.findall('EnumPair'):
            enum_id = ep.get('enumID')
            wire_value = ep.get('wireValue')
            if enum_id and wire_value is not None:
                pairs[enum_id] = wire_value
        return pairs

    def _extract_list_items(self, control_elem: ET.Element) -> List[Tuple[str, str]]:
        """Extract (enum_id, ui_rep) from ListItem children on a control."""
        items: List[Tuple[str, str]] = []
        for li in control_elem.findall('lay:ListItem', self.NAMESPACES) + control_elem.findall('ListItem'):
            enum_id = li.get('enumID')
            if not enum_id:
                continue
            ui_rep = li.get('uiRep') or enum_id
            items.append((enum_id, ui_rep))
        return items

    def _extract_controls(self, strategy_elem: ET.Element) -> List[Control]:
        """Extract all UI controls from a strategy."""
        controls = []
        row = 0
        col = 0

        control_elements = (
            strategy_elem.findall('.//lay:Control', self.NAMESPACES)
            + strategy_elem.findall('.//atdl:Control', self.NAMESPACES)
            + strategy_elem.findall('.//Control')
        )

        for index, control_elem in enumerate(control_elements):
            param_ref = control_elem.get('parameterRef')
            if not param_ref:
                continue

            label = control_elem.get('label', param_ref)
            control_type = control_elem.get(f'{{{self.NAMESPACES["xsi"]}}}type')
            help_text = control_elem.get('tooltip') or control_elem.get('help')
            enabled = control_elem.get('enabled', 'true').lower() == 'true'
            visible = control_elem.get('visible', 'true').lower() == 'true'

            # Simple two-column layout: label/value pairs occupy two grid columns.
            row = index // 2
            col = (index % 2) * 2

            control = Control(
                parameter_ref=param_ref,
                control_type=control_type or 'TextField_t',
                label=label,
                position=(row, col),
                help_text=help_text,
                enabled=enabled,
                visible=visible,
                list_items=self._extract_list_items(control_elem),
                init_value=control_elem.get('initValue'),
            )
            controls.append(control)

        return controls

    def _extract_state_rules(self, strategy_elem: ET.Element) -> List[Dict]:
        """Extract state rules (parse but don't evaluate in MVP)."""
        rules = []

        # Find StateRules elements
        for state_rules_elem in strategy_elem.findall('.//atdl:StateRules', self.NAMESPACES):
            for rule_elem in state_rules_elem.findall('atdl:StateRule', self.NAMESPACES):
                rule_name = rule_elem.get('name')
                enabled_expr = rule_elem.get('enabled')

                if rule_name and enabled_expr:
                    rules.append({
                        'name': rule_name,
                        'enabled': enabled_expr,
                    })

        return rules
