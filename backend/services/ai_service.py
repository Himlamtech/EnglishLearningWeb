"""
AI service for text processing operations.

This module provides AI-powered text processing services including
grammar checking, text enhancement, humanization, and AI detection.
"""

import logging
from typing import List, Dict, Any, Optional

from clients.openai_client import OpenAIClient
from utils.exceptions import ValidationException, APIException
from utils.validators import validate_text_input, validate_enhancement_task, validate_chat_messages
from utils.decorators import log_execution_time

logger = logging.getLogger(__name__)


class AIService:
    """
    Service class for AI-powered text processing operations.

    Handles grammar checking, text enhancement, humanization,
    AI detection, and language learning chat assistance.
    """

    def __init__(self):
        """Initialize the AI service."""
        self._ai_client: Optional[OpenAIClient] = None

    async def _get_ai_client(self) -> OpenAIClient:
        """Get or create AI client instance."""
        if self._ai_client is None:
            self._ai_client = OpenAIClient()
        return self._ai_client

    async def close(self) -> None:
        """Close any open connections."""
        if self._ai_client:
            await self._ai_client.close()
            self._ai_client = None

    @log_execution_time(logger)
    async def check_grammar(self, text: str) -> Dict[str, Any]:
        """
        Check grammar in the provided text using advanced AI analysis.

        Args:
            text: Text to check for grammar errors

        Returns:
            Dictionary containing corrected text and error list

        Raises:
            ValidationException: If input text is invalid
            APIException: If grammar checking fails
        """
        logger.info(f"Checking grammar for text: '{text[:50]}...'")

        try:
            # Validate input
            validated_text = validate_text_input(
                text,
                min_length=1,
                max_length=5000,
                field_name="text"
            )

            # Use AI client for grammar checking
            ai_client = await self._get_ai_client()
            result = await ai_client.check_grammar(validated_text)

            # Validate result
            if not isinstance(result, dict) or "correctedText" not in result:
                raise APIException(
                    "Invalid grammar check response from AI",
                    error_code="INVALID_AI_RESPONSE"
                )

            logger.info("Grammar check completed successfully")
            return {
                "correctedText": result.get("correctedText", validated_text),
                "errors": result.get("errors", ["No grammar errors found"])
            }

        except (ValidationException, APIException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in grammar check: {str(e)}")
            raise APIException(
                f"Grammar check failed: {str(e)}",
                error_code="GRAMMAR_CHECK_ERROR"
            )

    @log_execution_time(logger)
    async def enhance_text(self, text: str, task: str) -> str:
        """
        Enhance text based on the specified task using advanced AI.

        Args:
            text: Text to enhance
            task: Enhancement task (rewrite, paraphrase, enhance)

        Returns:
            Enhanced text

        Raises:
            ValidationException: If input is invalid
            APIException: If text enhancement fails
        """
        logger.info(f"Enhancing text with task '{task}': '{text[:50]}...'")

        try:
            # Validate inputs
            validated_text = validate_text_input(
                text,
                min_length=1,
                max_length=5000,
                field_name="text"
            )
            validated_task = validate_enhancement_task(task)

            # Use AI client for text enhancement
            ai_client = await self._get_ai_client()
            enhanced_text = await ai_client.enhance_text(validated_text, validated_task)

            # Validate result
            if not enhanced_text or not isinstance(enhanced_text, str):
                raise APIException(
                    "Invalid text enhancement response from AI",
                    error_code="INVALID_AI_RESPONSE"
                )

            logger.info(f"Text enhancement completed successfully for task '{task}'")
            return enhanced_text.strip()

        except (ValidationException, APIException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in text enhancement: {str(e)}")
            raise APIException(
                f"Text enhancement failed: {str(e)}",
                error_code="ENHANCEMENT_ERROR"
            )

    @log_execution_time(logger)
    async def humanize_text(self, text: str) -> str:
        """
        Make AI-generated text sound more human and natural.

        Args:
            text: AI-generated text to humanize

        Returns:
            Humanized text

        Raises:
            ValidationException: If input text is invalid
            APIException: If humanization fails
        """
        logger.info(f"Humanizing text: '{text[:50]}...'")

        try:
            # Validate input
            validated_text = validate_text_input(
                text,
                min_length=1,
                max_length=5000,
                field_name="text"
            )

            # Use AI client for text humanization
            ai_client = await self._get_ai_client()
            humanized_text = await ai_client.humanize_text(validated_text)

            # Validate result
            if not humanized_text or not isinstance(humanized_text, str):
                raise APIException(
                    "Invalid text humanization response from AI",
                    error_code="INVALID_AI_RESPONSE"
                )

            logger.info("Text humanization completed successfully")
            return humanized_text.strip()

        except (ValidationException, APIException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in text humanization: {str(e)}")
            raise APIException(
                f"Text humanization failed: {str(e)}",
                error_code="HUMANIZATION_ERROR"
            )

    @log_execution_time(logger)
    async def check_ai_probability(self, text: str) -> int:
        """
        Check the probability that text was generated by AI.

        Args:
            text: Text to analyze for AI generation probability

        Returns:
            Probability percentage (0-100)

        Raises:
            ValidationException: If input text is invalid
            APIException: If AI detection fails
        """
        logger.info(f"Checking AI probability for text: '{text[:50]}...'")

        try:
            # Validate input
            validated_text = validate_text_input(
                text,
                min_length=1,
                max_length=5000,
                field_name="text"
            )

            # Use AI client for AI probability detection
            ai_client = await self._get_ai_client()
            probability = await ai_client.check_ai_probability(validated_text)

            # Validate result
            if not isinstance(probability, int) or probability < 0 or probability > 100:
                logger.warning(f"Invalid AI probability result: {probability}, using default")
                probability = 50  # Default uncertain value

            logger.info(f"AI probability check completed: {probability}%")
            return probability

        except (ValidationException, APIException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in AI probability check: {str(e)}")
            raise APIException(
                f"AI probability check failed: {str(e)}",
                error_code="AI_DETECTION_ERROR"
            )

    @log_execution_time(logger)
    async def chat_with_ai(self, messages: List[Dict[str, str]]) -> str:
        """
        Chat with AI for language learning assistance.

        Args:
            messages: Conversation history

        Returns:
            AI response text

        Raises:
            ValidationException: If messages are invalid
            APIException: If chat fails
        """
        logger.info(f"Starting chat with {len(messages)} message(s)")

        try:
            # Validate messages
            validated_messages = validate_chat_messages(messages)

            # Use AI client for chat
            ai_client = await self._get_ai_client()
            response = await ai_client.chat_with_ai(validated_messages)

            # Validate result
            if not response or not isinstance(response, str):
                raise APIException(
                    "Invalid chat response from AI",
                    error_code="INVALID_AI_RESPONSE"
                )

            logger.info("Chat completed successfully")
            return response.strip()

        except (ValidationException, APIException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat: {str(e)}")
            raise APIException(
                f"Chat failed: {str(e)}",
                error_code="CHAT_ERROR"
            )

    @log_execution_time(logger)
    async def analyze_text_complexity(self, text: str) -> Dict[str, Any]:
        """
        Analyze text complexity for language learning purposes.

        Args:
            text: Text to analyze

        Returns:
            Dictionary containing complexity analysis

        Raises:
            ValidationException: If input text is invalid
        """
        logger.info(f"Analyzing text complexity: '{text[:50]}...'")

        try:
            # Validate input
            validated_text = validate_text_input(
                text,
                min_length=1,
                max_length=5000,
                field_name="text"
            )

            # Basic complexity analysis
            words = validated_text.split()
            sentences = validated_text.count('.') + validated_text.count('!') + validated_text.count('?')
            sentences = max(1, sentences)  # Avoid division by zero

            # Calculate metrics
            word_count = len(words)
            avg_word_length = sum(len(word.strip('.,!?;:')) for word in words) / word_count if word_count > 0 else 0
            avg_sentence_length = word_count / sentences

            # Determine complexity level
            if avg_word_length < 4 and avg_sentence_length < 10:
                complexity_level = "Beginner"
                difficulty_score = 1
            elif avg_word_length < 6 and avg_sentence_length < 15:
                complexity_level = "Intermediate"
                difficulty_score = 2
            else:
                complexity_level = "Advanced"
                difficulty_score = 3

            analysis = {
                "word_count": word_count,
                "sentence_count": sentences,
                "average_word_length": round(avg_word_length, 1),
                "average_sentence_length": round(avg_sentence_length, 1),
                "complexity_level": complexity_level,
                "difficulty_score": difficulty_score,
                "reading_time_minutes": round(word_count / 200, 1)  # Assuming 200 words per minute
            }

            logger.info(f"Text complexity analysis completed: {complexity_level} level")
            return analysis

        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in text complexity analysis: {str(e)}")
            raise APIException(
                f"Text complexity analysis failed: {str(e)}",
                error_code="COMPLEXITY_ANALYSIS_ERROR"
            )
