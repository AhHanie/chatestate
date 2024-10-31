from openai import OpenAI
import os
import json
from django.core.exceptions import ValidationError

from common.service_provider import ServiceProvider
from .service import EstateService
from .models import Estate


class RealEstateQueryProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.estate_service = ServiceProvider.get_service(EstateService)

    def _get_filters_from_query(self, query: str) -> dict:
        """
        Process natural language query to extract filters using ChatGPT.

        Args:
            query: Natural language query string

        Returns:
            dict: Extracted filters for database query
        """
        # Get the base prompt for filter extraction
        filters_prompt = self.estate_service.get_filters_ai_prompt(query)

        # Send query to OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4-0125-preview",  # Using GPT-4 for better understanding
            messages=[
                {
                    "role": "user",
                    "content": filters_prompt
                }
            ],
            temperature=0,  # Keep it deterministic for consistent filter extraction
            max_tokens=1024,
            response_format={"type": "json_object"}  # Ensure JSON response
        )

        try:
            # Parse the JSON response
            filters = json.loads(response.choices[0].message.content)
            return filters
        except json.JSONDecodeError:
            raise ValueError("Failed to parse AI-generated filters")

    def _generate_property_summary(self, properties: list, query: str) -> str:
        """
        Generate a natural language summary of matching properties using ChatGPT.

        Args:
            properties: List of matching Estate objects
            query: Original user query

        Returns:
            str: Generated summary
        """
        # Convert properties to JSON for the prompt
        properties_json = json.dumps([{
            'title': p.title,
            'description': p.description,
        } for p in properties])

        # Get the base prompt for summary generation
        summary_prompt = self.estate_service.get_summary_ai_prompt()

        # Send to OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4-0125-preview",  # Using GPT-4 for better quality summaries
            messages=[
                {
                    "role": "user",
                    "content": f"{summary_prompt}\n\nProperties: {properties_json}"
                }
            ],
            temperature=0.7,  # Allow some creativity in summary generation
            max_tokens=2048
        )

        return response.choices[0].message.content

    def process_query(self, query: str) -> dict:
        """
        Process a natural language real estate query end-to-end.

        Args:
            query: Natural language query string

        Returns:
            dict: Response containing summary and matched properties
        """
        try:
            # Extract filters from query
            filters = self._get_filters_from_query(query)

            # Validate filters
            self.estate_service.validate_filters(filters)

            # Query database with filters and get 5 random properties
            properties = Estate.objects.filter(**filters).order_by('?')[:5]

            if not properties:
                return {
                    "success": True,
                    "summary": "I apologize, but I couldn't find any properties matching your criteria.",
                }

            # Generate summary
            summary = self._generate_property_summary(properties, query)

            # Prepare response
            return {
                "success": True,
                "summary": summary
            }

        except ValidationError as e:
            return {
                "success": False,
                "error": f"Invalid filters: {str(e)}"
            }
        except ValueError as e:
            return {
                "success": False,
                "error": f"Processing error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
