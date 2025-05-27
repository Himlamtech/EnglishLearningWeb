# FlashAI Backend - Refactored Architecture

## Overview

This is the completely refactored FlashAI backend application, transformed from a basic prototype to a production-ready, scalable system with advanced AI prompt engineering capabilities.

## Key Features

### 🏗️ Clean Architecture
- **Service Layer**: Business logic separation
- **Repository Layer**: Data access abstraction
- **Client Layer**: External API integrations
- **Utils Layer**: Shared utilities and helpers

### 🤖 Advanced AI Prompt Engineering
- **Chain of Thought (CoT)**: Step-by-step reasoning
- **Tree of Thought (ToT)**: Structured branching logic
- **React (Reasoning + Acting)**: Combined reasoning and action methodology
- **Expert-level prompts** for all AI operations

### 🛡️ Robust Error Handling
- Custom exception hierarchy
- Comprehensive validation
- Structured error responses
- Detailed logging and monitoring

### 🔧 Production-Ready Features
- Automatic retry with exponential backoff
- Connection pooling and session management
- Input sanitization and security
- Configuration management
- Performance monitoring

## Quick Start

### Prerequisites
```bash
pip install fastapi uvicorn aiohttp python-dotenv pydantic
```

### Environment Setup
Create a `.env` file in the backend directory:
```env
OPENAI_API_KEY=your_api_key_here
API_BASE_URL=https://api.yescale.io
OPENAI_MODEL=gpt-4.1-nano-2025-04-14
DEBUG=false
LOG_LEVEL=INFO
```

### Running the Application
```bash
# Development mode
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Running Tests
```bash
python test_refactored_api.py
```

## API Endpoints

### Flashcard Management
- `POST /flashcards` - Create new flashcard with AI generation
- `GET /flashcards` - Get all flashcards
- `PUT /flashcards/{word}` - Update flashcard
- `DELETE /flashcards/{word}` - Delete flashcard
- `PUT /flashcards/{word}/learned` - Mark as learned/unlearned
- `GET /flashcards/statistics` - Get learning statistics
- `GET /flashcards/unlearned` - Get unlearned flashcards
- `GET /flashcards/learned` - Get learned flashcards
- `GET /flashcards/export` - Export to JSON
- `POST /flashcards/import` - Import from CSV

### AI Text Processing
- `POST /grammar-check` - Advanced grammar checking
- `POST /enhance-text` - Text enhancement (rewrite/paraphrase/enhance)
- `POST /humanize-text` - Make AI text sound human
- `POST /ai-probability` - Check if text is AI-generated
- `POST /chat` - Language learning chat assistance
- `POST /analyze-text` - Text complexity analysis

### System
- `GET /health` - Health check and system status

## Architecture Details

### Directory Structure
```
backend/
├── clients/
│   ├── __init__.py
│   └── openai_client.py          # Enhanced OpenAI client
├── repositories/
│   ├── __init__.py
│   └── flashcard_repository.py   # Data access layer
├── services/
│   ├── __init__.py
│   ├── flashcard_service.py      # Flashcard business logic
│   └── ai_service.py             # AI text processing logic
├── utils/
│   ├── __init__.py
│   ├── exceptions.py             # Custom exception classes
│   ├── decorators.py             # Utility decorators
│   ├── validators.py             # Input validation
│   └── prompt_templates.py       # Advanced AI prompts
├── config.py                     # Enhanced configuration
├── main.py                       # FastAPI application
├── models.py                     # Pydantic models
├── test_refactored_api.py        # Test suite
└── REFACTORING_SUMMARY.md        # Detailed refactoring documentation
```

### Key Components

#### Configuration (`config.py`)
- Centralized configuration management
- Environment variable support
- Validation and logging setup
- Type-safe configuration values

#### Custom Exceptions (`utils/exceptions.py`)
- `FlashAIException`: Base exception
- `APIException`: External API errors
- `ValidationException`: Input validation errors
- `StorageException`: Data access errors
- `ConfigurationException`: Configuration errors

#### Advanced Prompts (`utils/prompt_templates.py`)
- Expert-level prompt engineering
- CoT, ToT, and React methodologies
- Context-aware prompt generation
- Structured function calling

#### OpenAI Client (`clients/openai_client.py`)
- Production-ready API client
- Automatic retry and error handling
- Session management
- Response validation

#### Repository Layer (`repositories/`)
- Clean data access interface
- CSV file management
- CRUD operations
- Statistics and analytics

#### Service Layer (`services/`)
- Business logic separation
- Input validation
- AI integration
- Error handling

## Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key (required)
- `API_BASE_URL`: API base URL (default: https://api.yescale.io)
- `OPENAI_MODEL`: Model name (default: gpt-4.1-nano-2025-04-14)
- `DEFAULT_TIMEOUT`: Request timeout in seconds (default: 30)
- `MAX_RETRIES`: Maximum retry attempts (default: 3)
- `RETRY_DELAY`: Initial retry delay (default: 1.0)
- `DEFAULT_TEMPERATURE`: AI temperature (default: 0.3)
- `DEFAULT_MAX_TOKENS`: Max tokens per request (default: 800)
- `LOG_LEVEL`: Logging level (default: INFO)
- `DEBUG`: Debug mode (default: false)
- `CORS_ORIGINS`: Allowed CORS origins (default: *)

## Development

### Adding New Features
1. Create models in `models.py`
2. Add validation in `utils/validators.py`
3. Implement business logic in appropriate service
4. Add repository methods if needed
5. Create API endpoints in `main.py`
6. Add tests to verify functionality

### Testing
The test suite (`test_refactored_api.py`) covers:
- Configuration system
- Exception handling
- Input validation
- Prompt templates
- Repository operations
- Service layer
- Pydantic models

### Logging
Comprehensive logging is configured with:
- File and console output
- Configurable log levels
- Performance monitoring
- Error tracking with context

## Migration from Old Version

### Breaking Changes
- New directory structure
- Updated import paths
- Enhanced error responses
- Configuration changes

### Benefits
- 10x better error handling
- Advanced AI prompt engineering
- Production-ready architecture
- Comprehensive validation
- Performance monitoring
- Scalable design

## Contributing

1. Follow the established architecture patterns
2. Add comprehensive tests for new features
3. Use type hints throughout
4. Follow the existing code style
5. Update documentation as needed

## License

This project is part of the FlashAI English Learning Web application.
