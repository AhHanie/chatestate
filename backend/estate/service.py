from typing import Dict, Any, List, Tuple
from datetime import datetime
import pandas as pd
import re
import math
from django.core.exceptions import ValidationError

from .models import Types, Estate
from .constants import *
from .text_analyzer import TextAnalyzer
from .estate_filter_validator import EstateFilterValidator
from common.utils import first


class EstateService:
    def initTypes(self):
        """
        Initialize predefined types in the database for estate properties.

        This method populates the Types table with predefined values for:
        - Bathrooms (1-7, 7+, none)
        - Bedrooms (1-7, 7+, studio)
        - Estate Types (apartment, villa, townhouse, condo, mansion)
        - Furnishing Status (YES, NO, PARTLY)
        - Cities in UAE

        The method is idempotent - it only creates types that don't already exist,
        making it safe to run multiple times without creating duplicates.

        Returns:
            None

        Example:
            >>> EstateService.initTypes()
            # This will populate the Types table with all predefined values

        Note:
            - This method should be run when setting up the application
            - It's automatically called during application startup via apps.py
        """

        for t in INITIAL_TYPES:
            exists = Types.objects.filter(
                type=t['type'],
                value=t['value']
            ).exists()

            if not exists:
                new_type = Types(type=t['type'], value=t['value'])
                new_type.save()

        allTypes = Types.objects.all()
        di = {}
        for t in allTypes:
            if t.type == ESTATE_TYPE:
                di[t.value] = t.id

    def validate_filters(self, filters: Dict[str, Any]) -> None:
        """
        Validates estate filters using the EstateFilterValidator.

        Args:
            filters: Dictionary of filters to validate

        Raises:
            FilterValidationError: If any validation rule is violated
        """
        EstateFilterValidator.validate_filters(filters)

    def _convert_types_arr_to_dict_str(self, types: List[Types]):
        result = {}
        for item in types:
            result[item.value] = item.id
        return str(result)

    def get_filters_ai_prompt(self, query):
        bedroom_types = Types.objects.filter(type=BEDROOM_TYPE)
        bathroom_types = Types.objects.filter(type=BATHROOM_TYPE)
        estate_categories_types = Types.objects.filter(type=ESTATE_CATEGORY)
        furnishing_types = Types.objects.filter(type=FURNISHED_TYPE)
        city_types = Types.objects.filter(type=CITY_TYPE)
        estate_types = Types.objects.filter(type=ESTATE_TYPE)

        three_bedroom_type = first(bedroom_types, lambda x: x.value == '3')
        dubai_city_type = first(city_types, lambda x: x.value == 'Dubai')
        villa_estate_type = first(estate_types, lambda x: x.value == 'villa')

        return f"""
        You are an AI model assisting in developing an endpoint for a Django backend application. This endpoint will process natural language queries about real estate properties, extract relevant filters from the user's text, and then format these filters into a JSON object.

        The expected JSON output should contain only extracted filters as keys, with each key-value pair corresponding to the available filter criteria below:

        Filter Criteria:

        price: Numeric value only, representing the price in AED (Example: 800000).
        verified: Boolean indicating whether the property is verified.
        size: Numeric value only, representing the property size in square feet (Example: 1233).
        created_at: Date in ISO format (YYYY-MM-DD), assuming UTC (Example: "listed before 2024-10-05").
        bathrooms: Enum indicating the number of bathrooms (Map: {self._convert_types_arr_to_dict_str(bathroom_types)}).
        bedrooms: Enum indicating the number of bedrooms (Map: {self._convert_types_arr_to_dict_str(bedroom_types)}).
        furnished: Enum indicating furnishing status (Map: {self._convert_types_arr_to_dict_str(furnishing_types)}).
        category: Enum for estate category (Map: {self._convert_types_arr_to_dict_str(estate_categories_types)}).
        city: Enum indicating the estate's city (Map: {self._convert_types_arr_to_dict_str(city_types)}).
        type: Enum for estate type (Map: {self._convert_types_arr_to_dict_str(estate_types)}).
        Instructions:

        Range Queries: For filters that support range queries (e.g., price, size, created_at), add suffixes __gt or __lt to denote "greater than" or "less than" where appropriate. For example, "apartments costing more than 1,000,000 AED" should yield {{price__gt: 1000000 }}.
        Output: If filters are extracted successfully, format them into a JSON object, showing only the filters. If no filters are found, return an empty JSON object.
        Restrictions: Output only the JSON object, with no additional text or explanations.
        Example: Input: “Find me a 3-bedroom villa in Abu Dhabi.”

        Output: {{"bedrooms": {three_bedroom_type.id}, "city": {
            dubai_city_type.id}, "type": {villa_estate_type.id}}}

        User Query: {query}
        """

    def get_summary_ai_prompt():
        return 'You are a real estate agent. Given a JSON dataset of real estate properties, create a well-organized summary of the properties to present to a customer. Focus on clarity and professionalism, highlighting key details like property type, location, price, size, and unique features. Ensure the summary is concise, visually clean, and customer-friendly.'

    @staticmethod
    def _convert_to_boolean(value) -> bool:
        """Convert various string representations to boolean values"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.strip().upper()
            if value in ['YES', 'TRUE', '1', 'Y']:
                return True
            if value in ['NO', 'FALSE', '0', 'N']:
                return False
        raise ValueError(f"Cannot convert '{value}' to boolean")

    @staticmethod
    def _parse_datetime(value) -> datetime:
        """Convert ISO format string to datetime"""
        if pd.isna(value):
            return None
        try:
            return pd.to_datetime(value)
        except Exception as e:
            raise ValueError(
                f"Invalid datetime format. Expected ISO format: {str(e)}")

    @staticmethod
    def _parse_size(value) -> int:
        """Extract numeric value from size string (e.g., '1323 sqft' -> 1323)"""
        if pd.isna(value):
            raise ValueError("Size cannot be empty")
        if isinstance(value, (int, float)):
            return int(value)

        value = str(value).strip().lower()
        match = re.match(r'^(\d+)\s*sqft$', value)
        if match:
            return int(match.group(1))
        raise ValueError(
            f"Invalid size format. Expected 'X sqft', got '{value}'")

    @staticmethod
    def _parse_type_function_generator(allowed_values: List[Types], column_name: str) -> callable:
        """
        Generate a function that parses and validates type values against a predefined set of allowed values.

        This is a factory function that creates specialized parser functions for different type columns
        (e.g., bathrooms, bedrooms, furnishing status). The generated parser converts input values
        to corresponding type IDs from the database.

        Args:
            allowed_values (List[Types]): List of Type model instances representing valid values
                for this type category. Each Type instance should have 'value' and 'id' attributes.
            column_name (str): Name of the column being parsed. Used in error messages to help
                identify where validation failed.

        Returns:
            callable: A function that takes a single value and returns either:
                - The ID of the matching Type instance
                - None if the input is NaN
                - Raises ValueError if the input doesn't match any allowed values

        Examples:
            >>> # Creating a parser for bathroom types
            >>> bathroom_types = Types.objects.filter(type=BATHROOM_TYPE)
            >>> parse_bathroom = _parse_type_function_generator(bathroom_types, 'bathrooms')
            >>> 
            >>> # Using the generated parser
            >>> bathroom_id = parse_bathroom('2')  # Returns ID for '2 bathrooms' type
            >>> bathroom_id = parse_bathroom(float('nan'))  # Returns None
            >>> bathroom_id = parse_bathroom('invalid')  # Raises ValueError

        Raises:
            ValueError: If the input value doesn't match any allowed value in the type list

        Note:
            - The generated parser function handles pandas' NaN values by converting them to None
            - The comparison between input values and allowed values is case-sensitive
            - This is typically used when processing CSV uploads where type values need to be
              converted to their corresponding database IDs
        """
        def parse_type_column(value):
            # Try to find a matching type in our allowed values
            found_type = first(allowed_values, lambda x: x.value == value)

            if found_type:
                # If we found a matching type, return its ID
                return found_type.id
            elif math.isnan(value):
                # Handle pandas/numpy NaN values by converting to None
                # This allows for optional/nullable fields in the database
                return None
            else:
                # If value isn't NaN but also doesn't match any allowed values,
                # raise an error with a descriptive message
                raise ValueError(
                    f"Invalid value: '{value}' for column: {column_name}. "
                    f"Allowed values are: {
                        ', '.join(t.value for t in allowed_values)}"
                )

        # Return the generated parser function
        return parse_type_column

    @staticmethod
    def _remove_nan(value):
        if math.isnan(value):
            return None
        return value

    def process_estate_upload(self, csv_file, truncate: bool = False) -> Dict[str, Any]:
        """
        Process estate data upload from CSV file.

        Args:
            csv_file: CSV file containing estate data
            truncate: Whether to clear existing estates before import

        Returns:
            Dict containing upload results with success count and any errors

        Raises:
            ValueError: If file format or data is invalid
        """
        if truncate:
            Estate.objects.all().delete()

        # Load required type data
        bedroom_types = Types.objects.filter(type=BEDROOM_TYPE)
        bathroom_types = Types.objects.filter(type=BATHROOM_TYPE)
        estate_categories = Types.objects.filter(type=ESTATE_CATEGORY)
        furnishing_types = Types.objects.filter(type=FURNISHED_TYPE)
        city_types = Types.objects.filter(type=CITY_TYPE)
        estate_types = Types.objects.filter(type=ESTATE_TYPE)

        city_names = [x.value for x in city_types]
        estate_types_values = [x.value for x in estate_types]

        # Read CSV file
        df = pd.read_csv(csv_file)

        # Validate required columns
        required_columns = {
            'displayAddress': str,
            'bathrooms': str,
            'bedrooms': str,
            'price': int,
            'verified': str,
            'type': str,
            'priceDuration': str,
            'sizeMin': str,
            'furnishing': str,
            'description': str,
            'addedOn': str,
            'title': str
        }

        missing_columns = set(required_columns.keys()) - set(df.columns)
        if missing_columns:
            raise ValueError(f'Missing required columns: {
                             ", ".join(missing_columns)}')

        # Convert data types
        for column, dtype in required_columns.items():
            if column not in ['verified', 'furnishing', 'addedOn', 'sizeMin',
                              'bathrooms', 'bedrooms', 'type']:
                df[column] = df[column].astype(dtype)

        # Process special columns
        df['verified'] = df['verified'].apply(self._convert_to_boolean)
        df['addedOn'] = df['addedOn'].apply(self._parse_datetime)
        df['sizeMin'] = df['sizeMin'].apply(self._parse_size)

        # Convert type fields
        df['furnishing'] = df['furnishing'].apply(
            self._parse_type_function_generator(furnishing_types, 'furnishing'))
        df['type'] = df['type'].apply(
            self._parse_type_function_generator(estate_categories, 'type'))
        df['bathrooms'] = df['bathrooms'].apply(
            self._parse_type_function_generator(bathroom_types, 'bathrooms'))
        df['bedrooms'] = df['bedrooms'].apply(
            self._parse_type_function_generator(bedroom_types, 'bedrooms'))

        success_count = 0
        errors = []

        # Process each row
        for index, row in df.iterrows():
            try:
                estate = self._create_estate_from_row(row, city_types, estate_types,
                                                      city_names, estate_types_values)
                estate.full_clean()
                estate.save()
                success_count += 1
            except (ValidationError, Exception) as e:
                errors.append(f'Row {index + 2}: {str(e)}')

        return {
            'message': f'Successfully processed {success_count} records',
            'total_records': len(df),
            'successful_records': success_count,
            'failed_records': len(df) - success_count,
            'errors': errors if errors else None
        }

    def _create_estate_from_row(self, row, city_types, estate_types,
                                city_names, estate_types_values) -> Estate:
        """Create Estate instance from DataFrame row"""
        # Find city and estate type from text analysis
        city_id = None
        type_id = None

        city = TextAnalyzer.findMostFrequentPattern(
            row['title'] + ' ' + row['description'],
            city_names
        )
        if city:
            found_city_type = first(city_types, lambda x: x.value == city)
            if found_city_type:
                city_id = found_city_type.id

        estate_type = TextAnalyzer.findMostFrequentPattern(
            row['title'] + ' ' + row['description'],
            estate_types_values
        )
        if estate_type:
            found_estate_type = first(
                estate_types, lambda x: x.value == estate_type)
            if found_estate_type:
                type_id = found_estate_type.id

        # Create and return Estate instance
        return Estate(
            address=row['displayAddress'],
            bathrooms_id=self._remove_nan(row['bathrooms']),
            bedrooms_id=self._remove_nan(row['bedrooms']),
            price=row['price'],
            verified=row['verified'],
            category_id=self._remove_nan(row['type']),
            price_duration=row['priceDuration'],
            size=row['sizeMin'],
            furnished_id=self._remove_nan(row['furnishing']),
            description=row['description'],
            created_at=row['addedOn'],
            title=row['title'],
            city_id=city_id,
            type_id=type_id
        )
