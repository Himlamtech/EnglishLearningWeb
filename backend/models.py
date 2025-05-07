from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Flashcard(BaseModel):
    word: str
    translatedWord: str
    pronunciation: str
    synonyms: List[str]
    isLearned: bool = False
    createdAt: str = Field(default_factory=lambda: datetime.now().isoformat())

class FlashcardCreate(BaseModel):
    word: str
    targetLanguage: Optional[str] = "auto"

class TextInput(BaseModel):
    text: str

class EnhanceTextInput(BaseModel):
    text: str
    task: str = Field(..., description="Task type: 'rewrite', 'paraphrase', or 'enhance'")

class GrammarResponse(BaseModel):
    correctedText: str
    errors: List[str]

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatInput(BaseModel):
    messages: List[ChatMessage] 