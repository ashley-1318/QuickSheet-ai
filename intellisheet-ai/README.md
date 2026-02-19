# IntelliSheet AI

IntelliSheet AI is an AI-powered application designed to process and analyze documents, providing users with intelligent insights and cheat sheets. This project is built using Python 3.11 and the FastAPI framework, ensuring high performance and scalability.

## Project Structure

```
intellisheet-ai
├── src
│   ├── main.py                # Entry point of the application
│   ├── api
│   │   ├── v1
│   │   │   ├── endpoints
│   │   │   │   └── health.py  # Health check endpoint
│   │   │   └── router.py      # Main router for API endpoints
│   ├── core
│   │   ├── config.py          # Configuration settings
│   │   └── logging.py         # Logging setup
│   ├── services
│   │   └── __init__.py        # Services module initialization
│   ├── schemas
│   │   └── __init__.py        # Schemas module initialization
│   ├── models
│   │   └── __init__.py        # Models module initialization
│   └── types
│       └── __init__.py        # Types module initialization
├── tests
│   └── test_health.py         # Unit tests for health check
├── render.yaml                # Deployment configuration for Render
├── requirements.txt           # Project dependencies
├── pyproject.toml             # Project configuration
└── README.md                  # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd intellisheet-ai
   ```

2. **Create a virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   Ensure to set the required environment variables, such as `GROQ_API_KEY`, in your environment or in a `.env` file.

5. **Run the application:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

- **Health Check**
  - **Endpoint:** `/api/v1/health`
  - **Method:** GET
  - **Description:** Returns the health status of the application.

## Deployment

This application is configured for deployment on Render. The `render.yaml` file contains the necessary configuration for deploying the FastAPI application.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.