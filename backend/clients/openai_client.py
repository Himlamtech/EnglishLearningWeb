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

    def _parse_flashcard_from_text(self, text_response: str, word: str) -> Optional[Dict[str, Any]]:
        """
        Parse flashcard information from text response when function calling is not supported.

        Args:
            text_response: Text response from API
            word: Original word

        Returns:
            Parsed flashcard data or None
        """
        try:
            import re

            # Try to extract information using regex patterns
            # Look for translation patterns
            translation_patterns = [
                r'translation[:\s]*["\']?([^"\'\n]+)["\']?',
                r'translated[:\s]*["\']?([^"\'\n]+)["\']?',
                r'means[:\s]*["\']?([^"\'\n]+)["\']?',
                r'definition[:\s]*["\']?([^"\'\n]+)["\']?'
            ]

            translated_word = ""
            for pattern in translation_patterns:
                match = re.search(pattern, text_response, re.IGNORECASE)
                if match:
                    translated_word = match.group(1).strip()
                    break

            # Look for pronunciation patterns
            pronunciation_patterns = [
                r'pronunciation[:\s]*["\']?([^"\'\n]+)["\']?',
                r'IPA[:\s]*["\']?([^"\'\n]+)["\']?',
                r'/([^/]+)/',
                r'\[([^\]]+)\]'
            ]

            pronunciation = ""
            for pattern in pronunciation_patterns:
                match = re.search(pattern, text_response, re.IGNORECASE)
                if match:
                    pronunciation = match.group(1).strip()
                    break

            # Look for synonyms patterns
            synonyms_patterns = [
                r'synonyms[:\s]*\[([^\]]+)\]',
                r'synonyms[:\s]*([^.\n]+)',
                r'similar words[:\s]*([^.\n]+)'
            ]

            synonyms = []
            for pattern in synonyms_patterns:
                match = re.search(pattern, text_response, re.IGNORECASE)
                if match:
                    synonyms_text = match.group(1).strip()
                    # Split by common delimiters and clean up
                    synonyms = [s.strip().strip('"\'') for s in re.split(r'[,;]', synonyms_text)]
                    synonyms = [s for s in synonyms if s and len(s) > 1][:3]  # Take first 3
                    break

            # If we couldn't extract synonyms, provide some defaults
            if not synonyms:
                synonyms = ["similar", "equivalent", "related"]

            # Ensure we have at least basic information
            if not translated_word:
                # Try to extract any meaningful content as translation
                lines = text_response.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith(word) and len(line) < 50:
                        translated_word = line
                        break

                if not translated_word:
                    translated_word = "Translation not available"

            if not pronunciation:
                pronunciation = f"/{word}/"

            return {
                "word": word,
                "translatedWord": translated_word,
                "pronunciation": pronunciation,
                "synonyms": synonyms
            }

        except Exception as e:
            logger.error(f"Failed to parse flashcard from text: {str(e)}")
            return None

    async def _generate_flashcard_simple(self, word: str, target_language: str) -> Optional[Dict[str, Any]]:
        """
        Generate flashcard using a simple text-based prompt without function calling.

        Args:
            word: Word to create flashcard for
            target_language: Target language for translation

        Returns:
            Flashcard data dictionary or None
        """
        try:
            # Determine target language direction
            if target_language.lower() in ["vietnamese", "vi"]:
                lang_instruction = "Translate from English to Vietnamese"
            elif target_language.lower() in ["english", "en"]:
                lang_instruction = "Translate from Vietnamese to English"
            else:
                lang_instruction = "Auto-detect language and translate (English ↔ Vietnamese)"

            # Create a focused prompt for better results
            simple_prompt = f"""Create a language learning flashcard for: "{word}"

{lang_instruction}

Provide ONLY the following information in this exact format:
Translation: [accurate translation]
Pronunciation: [IPA notation]
Synonyms: [3 synonyms in source language, comma-separated]

Requirements:
- Translation must be accurate and commonly used
- Pronunciation in proper IPA format
- Synonyms must be in the same language as the original word
- Be concise and educational

Respond with ONLY the requested format, no explanations."""

            messages = [
                {"role": "system", "content": "You are an expert language tutor. Provide accurate, concise flashcard information. Follow the exact format requested without additional explanations."},
                {"role": "user", "content": simple_prompt}
            ]

            response = await self._make_api_request(messages=messages)
            text_response = self._extract_text_response(response)

            if text_response:
                return self._parse_flashcard_from_text(text_response, word)

            return None

        except Exception as e:
            logger.error(f"Failed to generate simple flashcard: {str(e)}")
            return None

    def _parse_grammar_from_text(self, text_response: str, original_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse grammar check information from text response when function calling is not supported.

        Args:
            text_response: Text response from API
            original_text: Original text that was checked

        Returns:
            Grammar check data or None
        """
        try:
            import re

            # Try to extract corrected text with better patterns
            corrected_patterns = [
                r'corrected text[:\s]*["\']?([^"\'\n]+)["\']?',
                r'corrected[:\s]*["\']?([^"\'\n]+)["\']?',
                r'correction[:\s]*["\']?([^"\'\n]+)["\']?',
                r'fixed[:\s]*["\']?([^"\'\n]+)["\']?'
            ]

            corrected_text = original_text  # Default to original
            for pattern in corrected_patterns:
                match = re.search(pattern, text_response, re.IGNORECASE)
                if match:
                    corrected_text = match.group(1).strip()
                    # Clean up common prefixes and suffixes
                    prefixes_to_remove = ['text:', 'the text:', 'sentence:']
                    for prefix in prefixes_to_remove:
                        if corrected_text.lower().startswith(prefix):
                            corrected_text = corrected_text[len(prefix):].strip()
                            break
                    # Remove quotes if present
                    corrected_text = corrected_text.strip('"\'')
                    break

            # If no pattern matched, try to find any sentence that looks like a correction
            if corrected_text == original_text:
                # Look for complete sentences in the response
                sentences = re.findall(r'[A-Z][^.!?]*[.!?]', text_response)
                for sentence in sentences:
                    # Skip sentences that contain "error" or "mistake"
                    if not re.search(r'\b(error|mistake|wrong|incorrect)\b', sentence, re.IGNORECASE):
                        # This might be the corrected version
                        corrected_text = sentence.strip()
                        break

            # Try to extract errors
            errors = []
            error_patterns = [
                r'errors?[:\s]*\[([^\]]+)\]',
                r'errors?[:\s]*([^.\n]+)',
                r'mistakes?[:\s]*([^.\n]+)',
                r'problems?[:\s]*([^.\n]+)'
            ]

            for pattern in error_patterns:
                match = re.search(pattern, text_response, re.IGNORECASE)
                if match:
                    errors_text = match.group(1).strip()
                    # Split by common delimiters and clean up
                    errors = [e.strip().strip('"\'') for e in re.split(r'[,;]', errors_text)]
                    errors = [e for e in errors if e and len(e) > 3]  # Filter out short entries
                    break

            # If no errors found, check if the text seems correct
            if not errors:
                if corrected_text.lower() == original_text.lower():
                    errors = ["No grammar errors found"]
                else:
                    errors = ["Grammar corrections applied"]

            return {
                "correctedText": corrected_text,
                "errors": errors
            }

        except Exception as e:
            logger.error(f"Failed to parse grammar from text: {str(e)}")
            return None

    async def _check_grammar_simple(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Check grammar using a simple text-based prompt without function calling.

        Args:
            text: Text to check for grammar errors

        Returns:
            Grammar check data dictionary or None
        """
        try:
            # Create a focused prompt for better grammar checking
            simple_prompt = f"""Check and correct the grammar in this text: "{text}"

Provide ONLY the following in this exact format:
Corrected Text: [the grammatically correct version]
Errors: [specific errors found, comma-separated]

Requirements:
- Fix ALL grammar, spelling, and punctuation errors
- Keep the original meaning and style
- List specific errors clearly (e.g., "subject-verb disagreement", "wrong tense")
- If no errors, write "No grammar errors found" for errors

Respond with ONLY the requested format, no explanations."""

            messages = [
                {"role": "system", "content": "You are an expert English grammar checker. Provide accurate corrections and identify specific errors. Follow the exact format requested without additional explanations."},
                {"role": "user", "content": simple_prompt}
            ]

            response = await self._make_api_request(messages=messages)
            text_response = self._extract_text_response(response)

            if text_response:
                return self._parse_grammar_from_text(text_response, text)

            return None

        except Exception as e:
            logger.error(f"Failed to check grammar with simple prompt: {str(e)}")
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

            # Try function calling first
            response = await self._make_api_request(
                messages=prompt_data["messages"],
                functions=prompt_data.get("functions"),
                function_call=prompt_data.get("function_call")
            )

            # Debug: Log the full response to understand the format
            logger.debug(f"Full API response: {json.dumps(response, indent=2)}")

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
                # Fallback: Try to parse the response as text and extract information
                logger.warning("Function call not supported, trying text-based fallback")
                text_response = self._extract_text_response(response)
                if text_response:
                    fallback_result = self._parse_flashcard_from_text(text_response, word)
                    if fallback_result:
                        logger.info(f"Successfully generated flashcard for '{word}' using text fallback")
                        return fallback_result

                # Final fallback: Try with a simpler text-based prompt
                logger.warning("Trying simplified text-based prompt")
                simple_response = await self._generate_flashcard_simple(word, target_language)
                if simple_response:
                    return simple_response

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

            # Debug: Log the full response to understand the format
            logger.debug(f"Full API response: {json.dumps(response, indent=2)}")

            # Extract function response
            function_result = self._extract_function_response(response)

            if function_result:
                logger.info("Grammar check completed successfully")
                return {
                    "correctedText": function_result.get("correctedText", text),
                    "errors": function_result.get("errors", ["No grammar errors found"])
                }
            else:
                # Fallback: Try to parse the response as text and extract information
                logger.warning("Function call not supported, trying text-based fallback")
                text_response = self._extract_text_response(response)
                if text_response:
                    fallback_result = self._parse_grammar_from_text(text_response, text)
                    if fallback_result:
                        logger.info("Grammar check completed successfully using text fallback")
                        return fallback_result

                # Final fallback: Try with a simpler text-based prompt
                logger.warning("Trying simplified text-based prompt for grammar check")
                simple_response = await self._check_grammar_simple(text)
                if simple_response:
                    return simple_response

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
