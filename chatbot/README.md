# AI Chatbot with Streamlit

A simple, elegant chatbot interface built with Streamlit that connects to an AI backend service. This application provides a user-friendly way to interact with AI models through a web interface.

## Features

- 🎯 Clean, intuitive user interface
- 💬 Real-time chat interactions
- 🔄 Automatic message history management
- ⚠️ Robust error handling
- 🔒 Environment-based configuration
- 🔄 Automatic retry mechanism for failed requests

1. Create a `.env` file in the project root directory:
```bash
touch .env
```

2. Configure your environment variables in the `.env` file:
```env
API_ENDPOINT=http://your-backend-url/query
MAX_RETRIES=3
RETRY_DELAY=1
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run chatbot.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

3. Start chatting with the AI by typing your message in the input field and pressing Enter

## Configuration

The application can be configured using the following environment variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `API_ENDPOINT` | URL of the backend API endpoint | `http://localhost:8000/estate/query` |
| `MAX_RETRIES` | Maximum number of retry attempts for failed requests | 3 |
| `RETRY_DELAY` | Delay (in seconds) between retry attempts | 1 |

## Project Structure

```
ai-chatbot/
├── chatbot.py          # Main application file
└── README.md          # Project documentation
```

## API Integration

The chatbot expects the backend API to handle POST requests with the following format:

### Request
```json
{
  "query": "user message"
}
```

### Response
```json
{
  "success": true,
  "summary": "AI response message",
  "error": null
}
```