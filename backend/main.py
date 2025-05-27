"""
Refactored FastAPI application with clean architecture.

This module provides the main FastAPI application with proper dependency injection,
error handling, and separation of concerns using the service layer pattern.
"""

import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import Config
from models import (
    Flashcard,
    FlashcardCreate,
    FlashcardUpdate,
    TextInput,
    EnhanceTextInput,
    GrammarResponse,
    ChatMessage,
    ChatInput
)
from services.flashcard_service import FlashcardService
from services.ai_service import AIService
from utils.exceptions import (
    FlashAIException,
    ValidationException,
    APIException,
    StorageException
)

logger = logging.getLogger(__name__)

# Global service instances
flashcard_service: FlashcardService = None
ai_service: AIService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    global flashcard_service, ai_service

    logger.info("Starting up FlashAI API server...")
    logger.info(f"API Key configured: {bool(Config.OPENAI_API_KEY)}")
    logger.info(f"API Base URL: {Config.API_BASE_URL}")
    logger.info(f"Model: {Config.OPENAI_MODEL}")

    # Initialize services
    flashcard_service = FlashcardService()
    ai_service = AIService()

    logger.info("Services initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down FlashAI API server...")

    # Close services
    if ai_service:
        await ai_service.close()
    if flashcard_service:
        await flashcard_service.close()

    logger.info("Services closed successfully")


# Create FastAPI app with lifespan management
app = FastAPI(
    title="FlashAI API",
    description="AI-powered flashcard and language learning application with advanced prompt engineering",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc: ValidationException):
    """Handle validation exceptions."""
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=400,
        content=exc.to_dict()
    )


@app.exception_handler(APIException)
async def api_exception_handler(request, exc: APIException):
    """Handle API exceptions."""
    logger.error(f"API error: {exc.message}")
    return JSONResponse(
        status_code=500,
        content=exc.to_dict()
    )


@app.exception_handler(StorageException)
async def storage_exception_handler(request, exc: StorageException):
    """Handle storage exceptions."""
    logger.error(f"Storage error: {exc.message}")
    return JSONResponse(
        status_code=500,
        content=exc.to_dict()
    )


# Dependency injection
def get_flashcard_service() -> FlashcardService:
    """Get flashcard service instance."""
    if flashcard_service is None:
        raise HTTPException(status_code=500, detail="Flashcard service not initialized")
    return flashcard_service


def get_ai_service() -> AIService:
    """Get AI service instance."""
    if ai_service is None:
        raise HTTPException(status_code=500, detail="AI service not initialized")
    return ai_service

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify API status."""
    return {
        "status": "ok",
        "message": "FlashAI API is running",
        "version": "2.0.0",
        "api_key_configured": bool(Config.OPENAI_API_KEY)
    }


# Flashcard endpoints
@app.post("/flashcards", response_model=Flashcard)
async def create_flashcard(
    flashcard_data: FlashcardCreate,
    service: FlashcardService = Depends(get_flashcard_service)
):
    """Create a new flashcard using AI generation."""
    result = await service.create_flashcard(flashcard_data)
    return Flashcard(**result)


@app.get("/flashcards", response_model=List[Flashcard])
async def get_all_flashcards(
    service: FlashcardService = Depends(get_flashcard_service)
):
    """Get all flashcards."""
    flashcards = service.get_all_flashcards()
    return [Flashcard(**f) for f in flashcards]


@app.put("/flashcards/{word}/learned", response_model=Dict[str, Any])
async def mark_flashcard_learned(
    word: str,
    is_learned: bool = True,
    service: FlashcardService = Depends(get_flashcard_service)
):
    """Mark a flashcard as learned or not learned."""
    service.mark_as_learned(word, is_learned)
    return {
        "success": True,
        "message": f"Flashcard marked as {'learned' if is_learned else 'not learned'}"
    }


@app.put("/flashcards/{word}", response_model=Flashcard)
async def update_flashcard(
    word: str,
    flashcard_data: FlashcardUpdate,
    service: FlashcardService = Depends(get_flashcard_service)
):
    """Update an existing flashcard."""
    updated_flashcard = service.update_flashcard(word, flashcard_data)
    return Flashcard(**updated_flashcard)


@app.delete("/flashcards/{word}", response_model=Dict[str, Any])
async def delete_flashcard(
    word: str,
    service: FlashcardService = Depends(get_flashcard_service)
):
    """Delete a flashcard."""
    service.delete_flashcard(word)
    return {"success": True, "message": f"Flashcard '{word}' deleted successfully"}


@app.get("/flashcards/export", response_model=Dict[str, Any])
async def export_flashcards(
    service: FlashcardService = Depends(get_flashcard_service)
):
    """Export all flashcards to JSON format."""
    json_data = service.export_flashcards()
    return {"data": json_data}


@app.post("/flashcards/import", response_model=Dict[str, Any])
async def import_flashcards(
    file_content: TextInput,
    service: FlashcardService = Depends(get_flashcard_service)
):
    """Import flashcards from CSV content."""
    service.import_flashcards(file_content.text)
    return {"success": True, "message": "Flashcards imported successfully"}


@app.get("/flashcards/statistics", response_model=Dict[str, Any])
async def get_learning_statistics(
    service: FlashcardService = Depends(get_flashcard_service)
):
    """Get learning statistics and progress information."""
    return service.get_learning_statistics()


@app.get("/flashcards/unlearned", response_model=List[Flashcard])
async def get_unlearned_flashcards(
    service: FlashcardService = Depends(get_flashcard_service)
):
    """Get all unlearned flashcards for study sessions."""
    flashcards = service.get_unlearned_flashcards()
    return [Flashcard(**f) for f in flashcards]


@app.get("/flashcards/learned", response_model=List[Flashcard])
async def get_learned_flashcards(
    service: FlashcardService = Depends(get_flashcard_service)
):
    """Get all learned flashcards for review sessions."""
    flashcards = service.get_learned_flashcards()
    return [Flashcard(**f) for f in flashcards]

# AI-powered text processing endpoints
@app.post("/grammar-check", response_model=GrammarResponse)
async def grammar_check(
    text_input: TextInput,
    service: AIService = Depends(get_ai_service)
):
    """Check grammar in the provided text using advanced AI analysis."""
    result = await service.check_grammar(text_input.text)
    return GrammarResponse(
        correctedText=result["correctedText"],
        errors=result["errors"]
    )


@app.post("/enhance-text", response_model=Dict[str, Any])
async def enhance_text(
    input_data: EnhanceTextInput,
    service: AIService = Depends(get_ai_service)
):
    """Enhance text based on the specified task using advanced AI."""
    result = await service.enhance_text(input_data.text, input_data.task)
    return {"enhancedText": result}


@app.post("/humanize-text", response_model=Dict[str, Any])
async def humanize_ai_text(
    text_input: TextInput,
    service: AIService = Depends(get_ai_service)
):
    """Make AI-generated text sound more human and natural."""
    result = await service.humanize_text(text_input.text)
    return {"humanizedText": result}


@app.post("/ai-probability", response_model=Dict[str, Any])
async def check_ai_text(
    text_input: TextInput,
    service: AIService = Depends(get_ai_service)
):
    """Check the probability that text was generated by AI."""
    probability = await service.check_ai_probability(text_input.text)
    return {"probability": probability}


@app.post("/chat", response_model=Dict[str, Any])
async def chat(
    chat_input: ChatInput,
    service: AIService = Depends(get_ai_service)
):
    """Chat with AI for language learning assistance."""
    messages = [{"role": msg.role, "content": msg.content} for msg in chat_input.messages]
    response = await service.chat_with_ai(messages)
    return {"response": response}


@app.post("/analyze-text", response_model=Dict[str, Any])
async def analyze_text_complexity(
    text_input: TextInput,
    service: AIService = Depends(get_ai_service)
):
    """Analyze text complexity for language learning purposes."""
    analysis = await service.analyze_text_complexity(text_input.text)
    return analysis


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)