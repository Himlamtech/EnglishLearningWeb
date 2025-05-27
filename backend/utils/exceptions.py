"""
Custom exceptions for the FlashAI application.

This module defines all custom exceptions used throughout the application
to provide better error handling and debugging capabilities.
"""

from typing import Optional, Dict, Any


class FlashAIException(Exception):
    """Base exception class for all FlashAI related errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class APIException(FlashAIException):
    """Exception raised when external API calls fail."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_data = response_data or {}


class ValidationException(FlashAIException):
    """Exception raised when input validation fails."""
    
    def __init__(
        self, 
        message: str, 
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value


class StorageException(FlashAIException):
    """Exception raised when storage operations fail."""
    
    def __init__(
        self, 
        message: str, 
        operation: Optional[str] = None,
        file_path: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.file_path = file_path


class ConfigurationException(FlashAIException):
    """Exception raised when configuration is invalid or missing."""
    
    def __init__(
        self, 
        message: str, 
        config_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.config_key = config_key


class PromptException(FlashAIException):
    """Exception raised when prompt generation or processing fails."""
    
    def __init__(
        self, 
        message: str, 
        prompt_type: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.prompt_type = prompt_type
        self.input_data = input_data or {}
