import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
import re
import math
import json
import traceback

from .constants import *
from common.utils import first
from .estate_query_processor import RealEstateQueryProcessor
from common.service_provider import ServiceProvider
from .service import EstateService

# Create your views here.


def index():
    return HttpResponse("Hello Word, This is estate")


def convert_to_boolean(value):
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


def parse_datetime(value):
    """Convert ISO format string to datetime"""
    if pd.isna(value):
        return None
    try:
        return pd.to_datetime(value)
    except Exception as e:
        raise ValueError(
            f"Invalid datetime format. Expected ISO format: {str(e)}")


def parse_size(value):
    """Extract numeric value from size string (e.g., '1323 sqft' -> 1323)"""
    if pd.isna(value):
        raise ValueError("Size cannot be empty")
    if isinstance(value, (int, float)):
        return int(value)

    value = str(value).strip().lower()
    match = re.match(r'^(\d+)\s*sqft$', value)
    if match:
        return int(match.group(1))
    raise ValueError(f"Invalid size format. Expected 'X sqft', got '{value}'")


def parseTypeFunctionGenerator(allowedValues, column_name):
    def parseTypeColumn(value):
        foundType = first(allowedValues, lambda x: x.value == value)
        if foundType:
            return foundType.id
        elif math.isnan(value):
            return None
        raise ValueError(f"Invalid value: '{value}' for column: {column_name}")
    return parseTypeColumn


def removeNan(value):
    if math.isnan(value):
        return None
    return value


@csrf_exempt
def upload_excel(request):
    """
    Handle estate data upload via CSV file.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    csv_file = request.FILES['file']

    # Check if it's a CSV file
    if not csv_file.name.endswith('.csv'):
        return JsonResponse({'error': 'File must be of type CSV'}, status=400)

    try:
        # Get estate service instance
        estate_service = ServiceProvider.get_service(EstateService)

        # Process the upload
        truncate = request.GET.get('truncate', 'false').lower() == 'true'
        result = estate_service.process_estate_upload(csv_file, truncate)

        return JsonResponse(result, status=200)

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error processing file: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def process_nlp_query(request):
    """
    Endpoint to handle natural language real estate queries.

    Expected POST body:
    {
        "query": "Find me a 3-bedroom villa in Dubai under 2 million AED"
    }
    """
    try:
        data = json.loads(request.body)
        query = data.get('query')

        if not query:
            return JsonResponse({
                "success": False,
                "error": "Query is required"
            }, status=400)

        processor = RealEstateQueryProcessor()
        result = processor.process_query(query)

        return JsonResponse(result, status=200 if result["success"] else 400)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON in request body"
        }, status=400)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            "success": False,
            "error": f"Server error: {str(e)}"
        }, status=500)
