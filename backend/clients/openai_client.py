"""
Enhanced OpenAI client with proper error handling, retry logic, and structured responses.

This module provides a clean, production-ready interface to the OpenAI API
with comprehensive error handling, retry mechanisms, and proper logging.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
import aiohttp

from config import Config
from utils.exceptions import APIException, ConfigurationException
from utils.decorators import retry_on_failure, log_execution_time, validate_api_key
from utils.prompt_templates import PromptTemplateEngine, PromptType

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Production-ready OpenAI API client with advanced features.

    Features:
    - Automatic retry with exponential backoff
    - Comprehensive error handling and logging
    - Session management and connection pooling
    - Structured prompt templates
    - Response validation and parsing
    """

    def __init__(self):
        """Initialize the OpenAI client."""
        self._session: Optional[aiohttp.ClientSession] = None
        self._prompt_engine = PromptTemplateEngine()

        # Validate configuration on initialization
        if not Config.OPENAI_API_KEY:
            raise ConfigurationException(
                "OpenAI API key is required but not configured",
                config_key="OPENAI_API_KEY"
            )

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure we have an active aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=Config.DEFAULT_TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    @retry_on_failure(
        max_retries=Config.MAX_RETRIES,
        delay=Config.RETRY_DELAY,
        exceptions=(aiohttp.ClientError, asyncio.TimeoutError, APIException)
    )
    @log_execution_time(logger)
    @validate_api_key
    async def _make_api_request(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Dict[str, str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the OpenAI API with proper error handling.

        Args:
            messages: List of conversation messages
            functions: Optional function definitions for function calling
            function_call: Optional function call specification
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            API response dictionary

        Raises:
            APIException: If the API request fails
        """
        session = await self._ensure_session()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.OPENAI_API_KEY}"
        }

        payload = {
            "model": Config.OPENAI_MODEL,
            "messages": messages,
            "temperature": temperature or Config.DEFAULT_TEMPERATURE,
            "max_tokens": max_tokens or Config.DEFAULT_MAX_TOKENS
        }

        if functions:
            payload["functions"] = functions
            logger.debug(f"Using {len(functions)} function(s) in API call")

        if function_call:
            payload["function_call"] = function_call
            logger.debug(f"Function call specified: {function_call}")

        logger.debug(f"Making API request to {Config.API_BASE_URL}/v1/chat/completions")

        try:
            async with session.post(
                f"{Config.API_BASE_URL}/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:

                response_text = await response.text()
                logger.debug(f"API response status: {response.status}")

                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        logger.info("API request completed successfully")
                        return result
                    except json.JSONDecodeError as e:
                        raise APIException(
                            f"Invalid JSON response from API: {str(e)}",
                            status_code=response.status,
                            response_data={"raw_response": response_text}
                        )
                else:
                    # Handle specific error status codes
                    error_message = self._parse_error_response(response.status, response_text)
                    raise APIException(
                        error_message,
                        status_code=response.status,
                        response_data={"raw_response": response_text}
                    )

        except aiohttp.ClientError as e:
            raise APIException(
                f"Network error during API request: {str(e)}",
                error_code="NETWORK_ERROR"
            )
        except asyncio.TimeoutError:
            raise APIException(
                f"API request timed out after {Config.DEFAULT_TIMEOUT} seconds",
                error_code="TIMEOUT_ERROR"
            )

    def _parse_error_response(self, status_code: int, response_text: str) -> str:
        """
        Parse error response and return appropriate error message.

        Args:
            status_code: HTTP status code
            response_text: Raw response text

        Returns:
            Formatted error message
        """
        error_messages = {
            400: "Bad request - invalid parameters",
            401: "Authentication failed - check API key",
            403: "Access forbidden - insufficient permissions",
            429: "Rate limit exceeded - too many requests",
            500: "Internal server error - try again later",
            502: "Bad gateway - service temporarily unavailable",
            503: "Service unavailable - try again later"
        }

        base_message = error_messages.get(status_code, f"API error (status {status_code})")

        # Try to extract more specific error information
        try:
            error_data = json.loads(response_text)
            if "error" in error_data and "message" in error_data["error"]:
                specific_message = error_data["error"]["message"]
                return f"{base_message}: {specific_message}"
        except (json.JSONDecodeError, KeyError):
            pass

        return f"{base_message}: {response_text[:200]}..."

    def _extract_function_response(self, api_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract function call response from API response.

        Args:
            api_response: Raw API response

        Returns:
            Parsed function arguments or None
        """
        try:
            if "choices" not in api_response or not api_response["choices"]:
                return None

            message = api_response["choices"][0]["message"]

            if "function_call" not in message or not message["function_call"]:
                return None

            function_call = message["function_call"]
            if "arguments" not in function_call:
                return None

            return json.loads(function_call["arguments"])

        except (KeyError, json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Failed to extract function response: {str(e)}")
            return None

    def _extract_text_response(self, api_response: Dict[str, Any]) -> Optional[str]:
        """
        Extract text content from API response.

        Args:
            api_response: Raw API response

        Returns:
            Response text content or None
        """
        try:
            if "choices" not in api_response or not api_response["choices"]:
                return None

            message = api_response["choices"][0]["message"]
            return message.get("content")

        except (KeyError, IndexError) as e:
            logger.warning(f"Failed to extract text response: {str(e)}")
            return None

    async def generate_flashcard(self, word: str, target_language: str = "auto") -> Dict[str, Any]:
        """
        Generate a flashcard for the given word using advanced prompts.

        Args:
            word: Word to create flashcard for
            target_language: Target language for translation

        Returns:
            Flashcard data dictionary

        Raises:
            APIException: If flashcard generation fails
        """
        logger.info(f"Generating flashcard for word: '{word}' (target: {target_language})")

        try:
            # Generate advanced prompt using the template engine
            prompt_data = self._prompt_engine.generate_flashcard_prompt(word, target_language)

            # Make API request
            response = await self._make_api_request(
                messages=prompt_data["messages"],
                functions=prompt_data["functions"],
                function_call=prompt_data["function_call"]
            )

            # Extract function response
            function_result = self._extract_function_response(response)

            if function_result:
                logger.info(f"Successfully generated flashcard for '{word}'")
                return {
                    "word": function_result.get("word", word),
                    "translatedWord": function_result.get("translatedWord", ""),
                    "pronunciation": function_result.get("pronunciation", ""),
                    "synonyms": function_result.get("synonyms", [])
                }
            else:
                raise APIException(
                    f"Failed to generate flashcard for '{word}': No valid function response",
                    error_code="INVALID_FUNCTION_RESPONSE"
                )

        except Exception as e:
            if isinstance(e, APIException):
                raise
            logger.error(f"Unexpected error generating flashcard for '{word}': {str(e)}")
            raise APIException(
                f"Flashcard generation failed: {str(e)}",
                error_code="GENERATION_ERROR"
            )

    async def check_grammar(self, text: str) -> Dict[str, Any]:
        """
        Check grammar in the provided text using advanced prompts.

        Args:
            text: Text to check for grammar errors

        Returns:
            Grammar check results dictionary

        Raises:
            APIException: If grammar checking fails
        """
        logger.info(f"Checking grammar for text: '{text[:50]}...'")

        try:
            # Generate advanced prompt using the template engine
            prompt_data = self._prompt_engine.generate_grammar_check_prompt(text)

            # Make API request
            response = await self._make_api_request(
                messages=prompt_data["messages"],
                functions=prompt_data["functions"],
                function_call=prompt_data["function_call"]
            )

            # Extract function response
            function_result = self._extract_function_response(response)

            if function_result:
                logger.info("Grammar check completed successfully")
                return {
                    "correctedText": function_result.get("correctedText", text),
                    "errors": function_result.get("errors", ["No grammar errors found"])
                }
            else:
                raise APIException(
                    "Failed to check grammar: No valid function response",
                    error_code="INVALID_FUNCTION_RESPONSE"
                )

        except Exception as e:
            if isinstance(e, APIException):
                raise
            logger.error(f"Unexpected error checking grammar: {str(e)}")
            raise APIException(
                f"Grammar check failed: {str(e)}",
                error_code="GRAMMAR_CHECK_ERROR"
            )

    async def enhance_text(self, text: str, task: str) -> str:
        """
        Enhance text based on the specified task using advanced prompts.

        Args:
            text: Text to enhance
            task: Enhancement task (rewrite, paraphrase, enhance)

        Returns:
            Enhanced text

        Raises:
            APIException: If text enhancement fails
        """
        logger.info(f"Enhancing text with task '{task}': '{text[:50]}...'")

        try:
            # Generate advanced prompt using the template engine
            prompt_data = self._prompt_engine.generate_text_enhancement_prompt(text, task)

            # Make API request
            response = await self._make_api_request(
                messages=prompt_data["messages"]
            )

            # Extract text response
            enhanced_text = self._extract_text_response(response)

            if enhanced_text:
                logger.info(f"Text enhancement completed successfully for task '{task}'")
                return enhanced_text.strip()
            else:
                raise APIException(
                    f"Failed to enhance text with task '{task}': No valid response",
                    error_code="INVALID_TEXT_RESPONSE"
                )

        except Exception as e:
            if isinstance(e, APIException):
                raise
            logger.error(f"Unexpected error enhancing text: {str(e)}")
            raise APIException(
                f"Text enhancement failed: {str(e)}",
                error_code="ENHANCEMENT_ERROR"
            )

    async def humanize_text(self, text: str) -> str:
        """
        Make AI-generated text sound more human and natural.

        Args:
            text: AI-generated text to humanize

        Returns:
            Humanized text

        Raises:
            APIException: If text humanization fails
        """
        logger.info(f"Humanizing text: '{text[:50]}...'")

        try:
            # Generate advanced prompt using the template engine
            prompt_data = self._prompt_engine.generate_humanization_prompt(text)

            # Make API request
            response = await self._make_api_request(
                messages=prompt_data["messages"]
            )

            # Extract text response
            humanized_text = self._extract_text_response(response)

            if humanized_text:
                logger.info("Text humanization completed successfully")
                return humanized_text.strip()
            else:
                raise APIException(
                    "Failed to humanize text: No valid response",
                    error_code="INVALID_TEXT_RESPONSE"
                )

        except Exception as e:
            if isinstance(e, APIException):
                raise
            logger.error(f"Unexpected error humanizing text: {str(e)}")
            raise APIException(
                f"Text humanization failed: {str(e)}",
                error_code="HUMANIZATION_ERROR"
            )

    async def check_ai_probability(self, text: str) -> int:
        """
        Check the probability that text was generated by AI.

        Args:
            text: Text to analyze for AI generation probability

        Returns:
            Probability percentage (0-100)

        Raises:
            APIException: If AI probability check fails
        """
        logger.info(f"Checking AI probability for text: '{text[:50]}...'")

        try:
            # Generate advanced prompt using the template engine
            prompt_data = self._prompt_engine.generate_ai_detection_prompt(text)

            # Make API request
            response = await self._make_api_request(
                messages=prompt_data["messages"]
            )

            # Extract text response
            response_text = self._extract_text_response(response)

            if response_text:
                # Extract probability number from response
                import re
                numbers = re.findall(r'\d+', response_text)
                if numbers:
                    probability = int(numbers[0])
                    # Ensure it's in valid range
                    probability = max(0, min(100, probability))
                    logger.info(f"AI probability check completed: {probability}%")
                    return probability
                else:
                    logger.warning("No probability number found in AI detection response")
                    return 50  # Default uncertain value
            else:
                raise APIException(
                    "Failed to check AI probability: No valid response",
                    error_code="INVALID_TEXT_RESPONSE"
                )

        except Exception as e:
            if isinstance(e, APIException):
                raise
            logger.error(f"Unexpected error checking AI probability: {str(e)}")
            raise APIException(
                f"AI probability check failed: {str(e)}",
                error_code="AI_DETECTION_ERROR"
            )

    async def chat_with_ai(self, messages: List[Dict[str, str]]) -> str:
        """
        Chat with AI for language learning assistance.

        Args:
            messages: Conversation history

        Returns:
            AI response text

        Raises:
            APIException: If chat fails
        """
        logger.info(f"Starting chat with {len(messages)} message(s)")

        try:
            # Generate advanced prompt using the template engine
            prompt_data = self._prompt_engine.generate_language_chat_prompt(messages)

            # Make API request
            response = await self._make_api_request(
                messages=prompt_data["messages"]
            )

            # Extract text response
            response_text = self._extract_text_response(response)

            if response_text:
                logger.info("Chat completed successfully")
                return response_text.strip()
            else:
                raise APIException(
                    "Failed to get chat response: No valid response",
                    error_code="INVALID_TEXT_RESPONSE"
                )

        except Exception as e:
            if isinstance(e, APIException):
                raise
            logger.error(f"Unexpected error in chat: {str(e)}")
            raise APIException(
                f"Chat failed: {str(e)}",
                error_code="CHAT_ERROR"
            )
