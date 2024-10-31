from datetime import datetime
from typing import Dict, Any
from django.core.exceptions import ValidationError


class FilterValidationError(ValidationError):
    pass


class EstateFilterValidator:
    # Define allowed suffixes for different field types
    NUMERIC_SUFFIXES = ['', '__gt', '__lt']
    EXACT_MATCH_SUFFIX = ['']
    DATE_SUFFIXES = ['__gt', '__lt']

    # Define valid fields and their constraints
    FIELD_CONSTRAINTS = {
        'price': {
            'type': int,
            'suffixes': NUMERIC_SUFFIXES,
            'required': False
        },
        'size': {
            'type': int,
            'suffixes': NUMERIC_SUFFIXES,
            'required': False
        },
        'verified': {
            'type': bool,
            'suffixes': EXACT_MATCH_SUFFIX,
            'required': False
        },
        'created_at': {
            'type': str,  # Will be validated as ISO date string
            'suffixes': DATE_SUFFIXES,
            'required': False
        },
        'bathrooms': {
            'type': int,
            'suffixes': EXACT_MATCH_SUFFIX,
            'required': False
        },
        'bedrooms': {
            'type': int,
            'suffixes': EXACT_MATCH_SUFFIX,
            'required': False
        },
        'furnished': {
            'type': int,
            'suffixes': EXACT_MATCH_SUFFIX,
            'required': False
        },
        'city': {
            'type': int,
            'suffixes': EXACT_MATCH_SUFFIX,
            'required': False
        },
        'category': {
            'type': int,
            'suffixes': EXACT_MATCH_SUFFIX,
            'required': False
        },
        'type': {
            'type': int,
            'suffixes': EXACT_MATCH_SUFFIX,
            'required': False
        }
    }

    @classmethod
    def _validate_field_name(cls, field: str) -> tuple[str, str]:
        """
        Validates a field name and extracts its base name and suffix.

        Args:
            field: The field name to validate (e.g., 'price__gt')

        Returns:
            tuple: (base_field_name, suffix)

        Raises:
            FilterValidationError: If the field name is invalid
        """
        # Split field into base name and suffix
        parts = field.split('__')
        base_field = parts[0]
        suffix = f"__{parts[1]}" if len(parts) > 1 else ''

        # Check if base field exists in constraints
        if base_field not in cls.FIELD_CONSTRAINTS:
            raise FilterValidationError(f"Invalid field name: {field}")

        # Check if suffix is valid for this field
        allowed_suffixes = cls.FIELD_CONSTRAINTS[base_field]['suffixes']
        if suffix not in allowed_suffixes:
            raise FilterValidationError(
                f"Invalid suffix '{suffix}' for field '{base_field}'. "
                f"Allowed suffixes are: {', '.join(allowed_suffixes)}"
            )

        return base_field, suffix

    @classmethod
    def _validate_date_string(cls, value: str) -> None:
        """
        Validates that a string is in ISO date format.

        Args:
            value: The string to validate

        Raises:
            FilterValidationError: If the string is not a valid ISO date
        """
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            raise FilterValidationError(
                f"Invalid date format: {
                    value}. Expected ISO format (e.g., '2024-01-01T00:00:00Z')"
            )

    @classmethod
    def _validate_value(cls, field: str, value: Any, field_type: type) -> None:
        """
        Validates a field value against its expected type.

        Args:
            field: The field name
            value: The value to validate
            field_type: The expected type

        Raises:
            FilterValidationError: If the value is invalid
        """
        if value is None:
            return

        if field_type == str and field.startswith('created_at'):
            cls._validate_date_string(value)
            return

        if not isinstance(value, field_type):
            try:
                # Attempt type conversion for numeric types
                if field_type in (int, float):
                    converted_value = field_type(value)
                    if converted_value <= 0:
                        raise FilterValidationError(
                            f"Value for {field} must be positive"
                        )
                elif field_type == bool:
                    if not isinstance(value, bool):
                        raise FilterValidationError(
                            f"Value for {field} must be a boolean"
                        )
            except (ValueError, TypeError):
                raise FilterValidationError(
                    f"Invalid type for {field}. Expected {
                        field_type.__name__}, got {type(value).__name__}"
                )

    @classmethod
    def validate_filters(cls, filters: Dict[str, Any]) -> None:
        """
        Validates a dictionary of filters according to predefined rules.

        Args:
            filters: Dictionary of filters to validate

        Raises:
            FilterValidationError: If any validation rule is violated
        """
        if not filters:
            raise FilterValidationError("At least one filter must be provided")

        # Track valid filters count
        valid_filters = 0

        # Validate each filter
        for field, value in filters.items():
            try:
                # Validate field name and suffix
                base_field, suffix = cls._validate_field_name(field)

                # Get expected type for this field
                field_type = cls.FIELD_CONSTRAINTS[base_field]['type']

                # Validate value
                cls._validate_value(field, value, field_type)

                valid_filters += 1

            except FilterValidationError as e:
                raise FilterValidationError(
                    f"Validation error for {field}: {str(e)}")

        if valid_filters == 0:
            raise FilterValidationError("No valid filters provided")
