from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import os
import asyncio

from models import (
    Flashcard,
    FlashcardCreate,
    TextInput,
    EnhanceTextInput,
    GrammarResponse,
    ChatMessage,
    ChatInput
)
from openai_client import (
    generate_flashcard,
    check_grammar,
    enhance_writing,
    humanize_text,
    check_ai_probability,
    chat_with_ai,
    close_session
)
import storage

# Create FastAPI app
app = FastAPI(
    title="FlashAI API",
    description="API for AI-powered flashcard and language learning application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}

# Flashcard endpoints
@app.post("/flashcards", response_model=Flashcard)
async def create_flashcard(flashcard_data: FlashcardCreate):
    try:
        # Generate flashcard using OpenAI
        result = await generate_flashcard(flashcard_data.word, flashcard_data.targetLanguage)

        # Create flashcard model
        flashcard = Flashcard(
            word=result["word"],
            translatedWord=result["translatedWord"],
            pronunciation=result["pronunciation"],
            synonyms=result["synonyms"],
            isLearned=False
        )

        # Save to storage
        storage.add_flashcard(flashcard.dict())

        return flashcard
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create flashcard: {str(e)}")

@app.get("/flashcards", response_model=List[Flashcard])
async def get_all_flashcards():
    try:
        flashcards = storage.get_flashcards()
        return flashcards
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get flashcards: {str(e)}")

@app.put("/flashcards/{word}/learned", response_model=dict)
async def mark_flashcard_learned(word: str, is_learned: bool = True):
    try:
        success = storage.mark_as_learned(word, is_learned)
        if not success:
            raise HTTPException(status_code=404, detail=f"Flashcard with word '{word}' not found")
        return {"success": True, "message": f"Flashcard marked as {'learned' if is_learned else 'not learned'}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update flashcard: {str(e)}")

@app.get("/flashcards/export", response_model=Dict)
async def export_flashcards():
    try:
        json_data = storage.export_to_json()
        return {"data": json_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export flashcards: {str(e)}")

@app.post("/flashcards/import", response_model=dict)
async def import_flashcards(file_content: TextInput):
    try:
        success = storage.import_from_csv(file_content.text)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid CSV format")
        return {"success": True, "message": "Flashcards imported successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import flashcards: {str(e)}")

# Grammar checking endpoint
@app.post("/grammar-check", response_model=GrammarResponse)
async def grammar_check(text_input: TextInput):
    try:
        result = await check_grammar(text_input.text)
        return GrammarResponse(
            correctedText=result["correctedText"],
            errors=result["errors"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grammar check failed: {str(e)}")

# Text enhancement endpoints
@app.post("/enhance-text", response_model=Dict)
async def enhance_text(input_data: EnhanceTextInput):
    try:
        result = await enhance_writing(input_data.text, input_data.task)
        return {"enhancedText": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text enhancement failed: {str(e)}")

# AI humanization endpoint
@app.post("/humanize-text", response_model=Dict)
async def humanize_ai_text(text_input: TextInput):
    try:
        result = await humanize_text(text_input.text)
        return {"humanizedText": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text humanization failed: {str(e)}")

# AI probability check endpoint
@app.post("/ai-probability", response_model=Dict)
async def check_ai_text(text_input: TextInput):
    try:
        probability = await check_ai_probability(text_input.text)
        return {"probability": probability}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI probability check failed: {str(e)}")

# Chatbot endpoint
@app.post("/chat", response_model=Dict)
async def chat(chat_input: ChatInput):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in chat_input.messages]
        response = await chat_with_ai(messages)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

# Event handlers for startup and shutdown
@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    print("Starting up the API server...")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    print("Shutting down the API server...")
    await close_session()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)