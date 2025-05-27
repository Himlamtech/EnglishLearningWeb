"""
Utility decorators for the FlashAI application.

This module provides decorators for common functionality like
retry logic, logging, and performance monitoring.
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Callable, Any, Optional, Type, Union

from utils.exceptions import APIException, FlashAIException


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator to retry function execution on failure.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Factor to multiply delay by after each retry
        exceptions: Tuple of exception types to catch and retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logging.error(
                            f"Function {func.__name__} failed after {max_retries} retries. "
                            f"Last error: {str(e)}"
                        )
                        raise

                    logging.warning(
                        f"Function {func.__name__} failed on attempt {attempt + 1}. "
                        f"Retrying in {current_delay}s. Error: {str(e)}"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor

            # This should never be reached, but just in case
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logging.error(
                            f"Function {func.__name__} failed after {max_retries} retries. "
                            f"Last error: {str(e)}"
                        )
                        raise

                    logging.warning(
                        f"Function {func.__name__} failed on attempt {attempt + 1}. "
                        f"Retrying in {current_delay}s. Error: {str(e)}"
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff_factor

            # This should never be reached, but just in case
            raise last_exception

        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def log_execution_time(
    logger: Optional[logging.Logger] = None,
    level: int = logging.INFO
) -> Callable:
    """
    Decorator to log function execution time.

    Args:
        logger: Logger instance to use (defaults to function's module logger)
        level: Logging level to use
    """
    def decorator(func: Callable) -> Callable:
        func_logger = logger or logging.getLogger(func.__module__)

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                func_logger.log(
                    level,
                    f"Function {func.__name__} executed successfully in {execution_time:.3f}s"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                func_logger.error(
                    f"Function {func.__name__} failed after {execution_time:.3f}s: {str(e)}"
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                func_logger.log(
                    level,
                    f"Function {func.__name__} executed successfully in {execution_time:.3f}s"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                func_logger.error(
                    f"Function {func.__name__} failed after {execution_time:.3f}s: {str(e)}"
                )
                raise

        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def validate_api_key(func: Callable) -> Callable:
    """
    Decorator to validate that API key is available before making API calls.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        from config import Config

        if not Config.OPENAI_API_KEY:
            raise APIException(
                "OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable.",
                error_code="MISSING_API_KEY"
            )

        return func(*args, **kwargs)

    return wrapper
