# Real Estate Backend API

A Django-based backend service that provides intelligent real estate property management and natural language query processing capabilities. The system uses OpenAI's GPT models to understand natural language queries and provide relevant property matches.

## 🚀 Features

- Natural language property search using AI
- Property data management through CSV uploads
- Intelligent property matching and filtering
- Property type and attribute management
- City and location detection from property descriptions
- Smart property summarization

## 🛠 Tech Stack

- Python 3.x
- Django 5.1.x
- OpenAI GPT-4

## 📋 Prerequisites

- Python 3.x installed
- OpenAI API key
- Virtual environment (recommended)

## 🔧 Installation

1. Create a `.env` file in the project root and add your environment variables:
```env
AZURE_OPENAI_API_KEY=your-api-key-here
OPENAI_API_VERSION=your-model-here
AZURE_OPENAI_ENDPOINT=your-endpoint-here
AZURE_OPENAI_DEPLOYMENT=your-deployment-here
```

2. Generate migrations for application:
```bash
python manage.py makemigrations estate
```

3. Run database migrations:
```bash
python manage.py migrate
```

## 🚦 Usage

### Starting the Server

```bash
python manage.py runserver
```

The server will start at `http://localhost:8000`

### Creating an admin user

```bash
python manage.py createsuperuser
```

Follow the interactive shell instructions to create an admin user which can be accessed at `http://localhost:8000/admin`

### API Endpoints

#### 1. Natural Language Property Query
```http
POST /estate/query
Content-Type: application/json

{
    "query": "Find me a 3-bedroom villa in Dubai under 2 million AED"
}
```

Response:
```json
{
    "success": true,
    "summary": "I found several properties matching your criteria..."
}
```

#### 2. Upload Property Data
```http
POST /estate/upload
Content-Type: multipart/form-data

file: your-properties.csv
```

Query Parameters:
- `truncate=true` (optional): Clear existing properties before import

## 🏗 Project Structure

```
backend/
├── estate/
│   ├── models.py           # Database models
│   ├── views.py           # API endpoints
│   ├── service.py         # Business logic
│   ├── constants.py       # Configuration constants
│   └── estate_query_processor.py  # NLP processing
├── common/
│   └── service_provider.py  # Service container
└── manage.py
```

## 📝 Key Components

### Estate Model
The main model representing a property with attributes like:
- Address
- Price
- Size
- Bedrooms/Bathrooms
- Property type
- Furnishing status
- Location

### Natural Language Processing
The system uses GPT-4 to:
1. Parse natural language queries into structured filters
2. Generate human-friendly summaries of matching properties

### Type Management
The system maintains predefined types for:
- Number of bedrooms/bathrooms
- Furnishing status
- Property types
- Cities
- Estate categories