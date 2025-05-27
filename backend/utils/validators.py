"""
Input validation utilities for the FlashAI application.

This module provides validation functions for various input types
to ensure data integrity and security.
"""

import re
from typing import Optional, List, Dict, Any

from .exceptions import ValidationException


def validate_text_input(
    text: str, 
    min_length: int = 1, 
    max_length: int = 10000,
    field_name: str = "text"
) -> str:
    """
    Validate text input for length and content.
    
    Args:
        text: Text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        field_name: Name of the field for error messages
    
    Returns:
        Cleaned text
    
    Raises:
        ValidationException: If validation fails
    """
    if not isinstance(text, str):
        raise ValidationException(
            f"{field_name} must be a string",
            field=field_name,
            value=text
        )
    
    # Strip whitespace
    text = text.strip()
    
    if len(text) < min_length:
        raise ValidationException(
            f"{field_name} must be at least {min_length} characters long",
            field=field_name,
            value=text
        )
    
    if len(text) > max_length:
        raise ValidationException(
            f"{field_name} must be no more than {max_length} characters long",
            field=field_name,
            value=text
        )
    
    # Check for potentially malicious content
    if _contains_suspicious_patterns(text):
        raise ValidationException(
            f"{field_name} contains potentially unsafe content",
            field=field_name,
            value=text
        )
    
    return text


def validate_language_code(
    language_code: str,
    allowed_languages: Optional[List[str]] = None
) -> str:
    """
    Validate language code format and value.
    
    Args:
        language_code: Language code to validate
        allowed_languages: List of allowed language codes
    
    Returns:
        Normalized language code
    
    Raises:
        ValidationException: If validation fails
    """
    if not isinstance(language_code, str):
        raise ValidationException(
            "Language code must be a string",
            field="language_code",
            value=language_code
        )
    
    # Normalize to lowercase
    language_code = language_code.lower().strip()
    
    # Allow 'auto' as a special case
    if language_code == "auto":
        return language_code
    
    # Default allowed languages
    if allowed_languages is None:
        allowed_languages = [
            "en", "english",
            "vi", "vietnamese", 
            "auto"
        ]
    
    if language_code not in allowed_languages:
        raise ValidationException(
            f"Language code '{language_code}' is not supported. "
            f"Allowed values: {', '.join(allowed_languages)}",
            field="language_code",
            value=language_code
        )
    
    return language_code


def validate_word_input(word: str) -> str:
    """
    Validate word input for flashcard generation.
    
    Args:
        word: Word to validate
    
    Returns:
        Cleaned word
    
    Raises:
        ValidationException: If validation fails
    """
    word = validate_text_input(word, min_length=1, max_length=100, field_name="word")
    
    # Check if word contains only valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-ZàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđĐ\s\-']+$", word):
        raise ValidationException(
            "Word contains invalid characters. Only letters, spaces, hyphens, and apostrophes are allowed.",
            field="word",
            value=word
        )
    
    return word


def validate_enhancement_task(task: str) -> str:
    """
    Validate text enhancement task type.
    
    Args:
        task: Task type to validate
    
    Returns:
        Validated task type
    
    Raises:
        ValidationException: If validation fails
    """
    if not isinstance(task, str):
        raise ValidationException(
            "Task must be a string",
            field="task",
            value=task
        )
    
    task = task.lower().strip()
    allowed_tasks = ["rewrite", "paraphrase", "enhance"]
    
    if task not in allowed_tasks:
        raise ValidationException(
            f"Task '{task}' is not supported. Allowed values: {', '.join(allowed_tasks)}",
            field="task",
            value=task
        )
    
    return task


def validate_chat_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Validate chat messages format and content.
    
    Args:
        messages: List of chat messages to validate
    
    Returns:
        Validated messages
    
    Raises:
        ValidationException: If validation fails
    """
    if not isinstance(messages, list):
        raise ValidationException(
            "Messages must be a list",
            field="messages",
            value=messages
        )
    
    if len(messages) == 0:
        raise ValidationException(
            "Messages list cannot be empty",
            field="messages",
            value=messages
        )
    
    if len(messages) > 50:  # Reasonable limit for conversation history
        raise ValidationException(
            "Too many messages in conversation (max 50)",
            field="messages",
            value=messages
        )
    
    validated_messages = []
    allowed_roles = ["user", "assistant", "system"]
    
    for i, message in enumerate(messages):
        if not isinstance(message, dict):
            raise ValidationException(
                f"Message at index {i} must be a dictionary",
                field=f"messages[{i}]",
                value=message
            )
        
        if "role" not in message or "content" not in message:
            raise ValidationException(
                f"Message at index {i} must have 'role' and 'content' fields",
                field=f"messages[{i}]",
                value=message
            )
        
        role = message["role"]
        content = message["content"]
        
        if role not in allowed_roles:
            raise ValidationException(
                f"Invalid role '{role}' at message {i}. Allowed roles: {', '.join(allowed_roles)}",
                field=f"messages[{i}].role",
                value=role
            )
        
        content = validate_text_input(content, min_length=1, max_length=2000, field_name=f"messages[{i}].content")
        
        validated_messages.append({
            "role": role,
            "content": content
        })
    
    return validated_messages


def _contains_suspicious_patterns(text: str) -> bool:
    """
    Check if text contains potentially suspicious patterns.
    
    Args:
        text: Text to check
    
    Returns:
        True if suspicious patterns are found
    """
    # Patterns that might indicate injection attempts or malicious content
    suspicious_patterns = [
        r'<script[^>]*>',  # Script tags
        r'javascript:',     # JavaScript URLs
        r'data:text/html',  # Data URLs with HTML
        r'vbscript:',      # VBScript URLs
        r'on\w+\s*=',      # Event handlers
        r'eval\s*\(',      # eval() calls
        r'exec\s*\(',      # exec() calls
    ]
    
    text_lower = text.lower()
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    
    return False
