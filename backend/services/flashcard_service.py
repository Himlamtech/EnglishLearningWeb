"""
Business logic service for flashcard operations.

This module contains all business logic related to flashcard management,
including creation, retrieval, updates, and learning progress tracking.
"""

import logging
from typing import List, Dict, Any, Optional

from clients.openai_client import OpenAIClient
from repositories.flashcard_repository import FlashcardRepository
from utils.exceptions import ValidationException, APIException, StorageException
from utils.validators import validate_word_input, validate_language_code, validate_text_input
from utils.decorators import log_execution_time
from models import Flashcard, FlashcardCreate, FlashcardUpdate

logger = logging.getLogger(__name__)


class FlashcardService:
    """
    Service class for flashcard business logic.

    Handles all flashcard-related operations including AI generation,
    storage management, and learning progress tracking.
    """

    def __init__(self, repository: Optional[FlashcardRepository] = None):
        """
        Initialize the flashcard service.

        Args:
            repository: Optional custom repository instance
        """
        self.repository = repository or FlashcardRepository()
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
    async def create_flashcard(self, flashcard_data: FlashcardCreate) -> Dict[str, Any]:
        """
        Create a new flashcard using AI generation.

        Args:
            flashcard_data: Flashcard creation data

        Returns:
            Created flashcard dictionary

        Raises:
            ValidationException: If input data is invalid
            APIException: If AI generation fails
            StorageException: If storage fails
        """
        logger.info(f"Creating flashcard for word: '{flashcard_data.word}'")

        try:
            # Validate input
            word = validate_word_input(flashcard_data.word)
            target_language = validate_language_code(flashcard_data.targetLanguage or "auto")

            # Check if flashcard already exists
            existing_flashcard = self.repository.find_by_word(word)
            if existing_flashcard:
                logger.warning(f"Flashcard for word '{word}' already exists")
                raise ValidationException(
                    f"Flashcard for word '{word}' already exists",
                    field="word",
                    value=word
                )

            # Generate flashcard using AI
            ai_client = await self._get_ai_client()
            ai_result = await ai_client.generate_flashcard(word, target_language)

            # Validate AI result
            if not ai_result.get("translatedWord"):
                raise APIException(
                    "AI failed to generate a valid translation",
                    error_code="INVALID_AI_RESULT"
                )

            # Create flashcard data
            flashcard_dict = {
                "word": ai_result.get("word", word),
                "translatedWord": ai_result.get("translatedWord", ""),
                "pronunciation": ai_result.get("pronunciation", ""),
                "synonyms": ai_result.get("synonyms", []),
                "isLearned": False
            }

            # Save to repository
            success = self.repository.add(flashcard_dict)
            if not success:
                raise StorageException(
                    "Failed to save flashcard to storage",
                    operation="add"
                )

            logger.info(f"Successfully created flashcard for word: '{word}'")
            return flashcard_dict

        except (ValidationException, APIException, StorageException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating flashcard: {str(e)}")
            raise APIException(
                f"Failed to create flashcard: {str(e)}",
                error_code="CREATION_ERROR"
            )

    @log_execution_time(logger)
    def get_all_flashcards(self) -> List[Dict[str, Any]]:
        """
        Get all flashcards from storage.

        Returns:
            List of flashcard dictionaries

        Raises:
            StorageException: If retrieval fails
        """
        logger.info("Retrieving all flashcards")

        try:
            flashcards = self.repository.get_all()
            logger.info(f"Successfully retrieved {len(flashcards)} flashcards")
            return flashcards

        except StorageException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving flashcards: {str(e)}")
            raise StorageException(
                f"Failed to retrieve flashcards: {str(e)}",
                operation="get_all"
            )

    @log_execution_time(logger)
    def update_flashcard(self, word: str, update_data: FlashcardUpdate) -> Dict[str, Any]:
        """
        Update an existing flashcard.

        Args:
            word: Word to identify the flashcard
            update_data: Data to update

        Returns:
            Updated flashcard dictionary

        Raises:
            ValidationException: If input data is invalid
            StorageException: If update fails
        """
        logger.info(f"Updating flashcard for word: '{word}'")

        try:
            # Validate word
            word = validate_word_input(word)

            # Convert update data to dict, excluding unset values
            update_dict = update_data.dict(exclude_unset=True)

            # Validate updated word if provided
            if "word" in update_dict:
                update_dict["word"] = validate_word_input(update_dict["word"])

            # Validate translated word if provided
            if "translatedWord" in update_dict:
                update_dict["translatedWord"] = validate_text_input(
                    update_dict["translatedWord"],
                    min_length=1,
                    max_length=200,
                    field_name="translatedWord"
                )

            # Update in repository
            success = self.repository.update(word, update_dict)
            if not success:
                raise ValidationException(
                    f"Flashcard with word '{word}' not found",
                    field="word",
                    value=word
                )

            # Get updated flashcard
            updated_flashcard = self.repository.find_by_word(update_dict.get("word", word))
            if not updated_flashcard:
                raise StorageException(
                    "Failed to retrieve updated flashcard",
                    operation="find"
                )

            logger.info(f"Successfully updated flashcard for word: '{word}'")
            return updated_flashcard

        except (ValidationException, StorageException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating flashcard: {str(e)}")
            raise StorageException(
                f"Failed to update flashcard: {str(e)}",
                operation="update"
            )

    @log_execution_time(logger)
    def delete_flashcard(self, word: str) -> bool:
        """
        Delete a flashcard.

        Args:
            word: Word to identify the flashcard

        Returns:
            True if successful

        Raises:
            ValidationException: If word is invalid or flashcard not found
            StorageException: If deletion fails
        """
        logger.info(f"Deleting flashcard for word: '{word}'")

        try:
            # Validate word
            word = validate_word_input(word)

            # Delete from repository
            success = self.repository.delete(word)
            if not success:
                raise ValidationException(
                    f"Flashcard with word '{word}' not found",
                    field="word",
                    value=word
                )

            logger.info(f"Successfully deleted flashcard for word: '{word}'")
            return True

        except (ValidationException, StorageException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting flashcard: {str(e)}")
            raise StorageException(
                f"Failed to delete flashcard: {str(e)}",
                operation="delete"
            )

    @log_execution_time(logger)
    def mark_as_learned(self, word: str, is_learned: bool = True) -> bool:
        """
        Mark a flashcard as learned or not learned.

        Args:
            word: Word to identify the flashcard
            is_learned: Whether the flashcard is learned

        Returns:
            True if successful

        Raises:
            ValidationException: If word is invalid or flashcard not found
            StorageException: If update fails
        """
        logger.info(f"Marking flashcard '{word}' as {'learned' if is_learned else 'not learned'}")

        try:
            # Validate word
            word = validate_word_input(word)

            # Update in repository
            success = self.repository.mark_as_learned(word, is_learned)
            if not success:
                raise ValidationException(
                    f"Flashcard with word '{word}' not found",
                    field="word",
                    value=word
                )

            logger.info(f"Successfully marked flashcard '{word}' as {'learned' if is_learned else 'not learned'}")
            return True

        except (ValidationException, StorageException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error marking flashcard as learned: {str(e)}")
            raise StorageException(
                f"Failed to mark flashcard as learned: {str(e)}",
                operation="mark_learned"
            )

    @log_execution_time(logger)
    def export_flashcards(self) -> str:
        """
        Export all flashcards to JSON format.

        Returns:
            JSON string containing all flashcards

        Raises:
            StorageException: If export fails
        """
        logger.info("Exporting flashcards to JSON")

        try:
            json_data = self.repository.export_to_json()
            logger.info("Successfully exported flashcards to JSON")
            return json_data

        except StorageException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error exporting flashcards: {str(e)}")
            raise StorageException(
                f"Failed to export flashcards: {str(e)}",
                operation="export"
            )

    @log_execution_time(logger)
    def import_flashcards(self, csv_content: str) -> bool:
        """
        Import flashcards from CSV content.

        Args:
            csv_content: CSV content as string

        Returns:
            True if successful

        Raises:
            ValidationException: If CSV format is invalid
            StorageException: If import fails
        """
        logger.info("Importing flashcards from CSV")

        try:
            # Validate CSV content
            csv_content = validate_text_input(
                csv_content,
                min_length=10,
                max_length=1000000,  # 1MB limit
                field_name="csv_content"
            )

            # Import using repository
            success = self.repository.import_from_csv(csv_content)
            if not success:
                raise ValidationException(
                    "Invalid CSV format or content",
                    field="csv_content"
                )

            logger.info("Successfully imported flashcards from CSV")
            return True

        except (ValidationException, StorageException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error importing flashcards: {str(e)}")
            raise StorageException(
                f"Failed to import flashcards: {str(e)}",
                operation="import"
            )

    @log_execution_time(logger)
    def get_learning_statistics(self) -> Dict[str, Any]:
        """
        Get learning statistics and progress information.

        Returns:
            Dictionary containing learning statistics

        Raises:
            StorageException: If statistics generation fails
        """
        logger.info("Generating learning statistics")

        try:
            statistics = self.repository.get_statistics()

            # Add additional calculated metrics
            total = statistics['total_flashcards']
            learned = statistics['learned_flashcards']

            if total > 0:
                # Calculate learning efficiency (learned per day if we have date range)
                if statistics['earliest_creation_date'] and statistics['latest_creation_date']:
                    from datetime import datetime
                    try:
                        earliest = datetime.fromisoformat(statistics['earliest_creation_date'])
                        latest = datetime.fromisoformat(statistics['latest_creation_date'])
                        days_diff = (latest - earliest).days + 1  # +1 to include both days

                        statistics['average_flashcards_per_day'] = round(total / days_diff, 1)
                        statistics['average_learned_per_day'] = round(learned / days_diff, 1)
                    except ValueError:
                        # Handle invalid date formats
                        statistics['average_flashcards_per_day'] = 0
                        statistics['average_learned_per_day'] = 0
                else:
                    statistics['average_flashcards_per_day'] = 0
                    statistics['average_learned_per_day'] = 0

                # Learning recommendations
                if statistics['learning_progress_percentage'] < 25:
                    recommendation = "Keep practicing! Focus on reviewing your flashcards regularly."
                elif statistics['learning_progress_percentage'] < 50:
                    recommendation = "Good progress! Try to review learned cards periodically to maintain retention."
                elif statistics['learning_progress_percentage'] < 75:
                    recommendation = "Great work! You're making excellent progress. Keep it up!"
                else:
                    recommendation = "Outstanding! Consider adding more challenging vocabulary to continue growing."

                statistics['learning_recommendation'] = recommendation
            else:
                statistics['average_flashcards_per_day'] = 0
                statistics['average_learned_per_day'] = 0
                statistics['learning_recommendation'] = "Start by creating your first flashcard!"

            logger.info("Successfully generated learning statistics")
            return statistics

        except StorageException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating statistics: {str(e)}")
            raise StorageException(
                f"Failed to generate learning statistics: {str(e)}",
                operation="statistics"
            )

    @log_execution_time(logger)
    def find_flashcard(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Find a specific flashcard by word.

        Args:
            word: Word to search for

        Returns:
            Flashcard dictionary if found, None otherwise

        Raises:
            ValidationException: If word is invalid
            StorageException: If search fails
        """
        logger.info(f"Finding flashcard for word: '{word}'")

        try:
            # Validate word
            word = validate_word_input(word)

            # Search in repository
            flashcard = self.repository.find_by_word(word)

            if flashcard:
                logger.info(f"Found flashcard for word: '{word}'")
            else:
                logger.info(f"No flashcard found for word: '{word}'")

            return flashcard

        except (ValidationException, StorageException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error finding flashcard: {str(e)}")
            raise StorageException(
                f"Failed to find flashcard: {str(e)}",
                operation="find"
            )

    @log_execution_time(logger)
    def get_unlearned_flashcards(self) -> List[Dict[str, Any]]:
        """
        Get all unlearned flashcards for study sessions.

        Returns:
            List of unlearned flashcard dictionaries

        Raises:
            StorageException: If retrieval fails
        """
        logger.info("Retrieving unlearned flashcards")

        try:
            all_flashcards = self.repository.get_all()
            unlearned_flashcards = [f for f in all_flashcards if not f['isLearned']]

            logger.info(f"Found {len(unlearned_flashcards)} unlearned flashcards")
            return unlearned_flashcards

        except StorageException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving unlearned flashcards: {str(e)}")
            raise StorageException(
                f"Failed to retrieve unlearned flashcards: {str(e)}",
                operation="get_unlearned"
            )

    @log_execution_time(logger)
    def get_learned_flashcards(self) -> List[Dict[str, Any]]:
        """
        Get all learned flashcards for review sessions.

        Returns:
            List of learned flashcard dictionaries

        Raises:
            StorageException: If retrieval fails
        """
        logger.info("Retrieving learned flashcards")

        try:
            all_flashcards = self.repository.get_all()
            learned_flashcards = [f for f in all_flashcards if f['isLearned']]

            logger.info(f"Found {len(learned_flashcards)} learned flashcards")
            return learned_flashcards

        except StorageException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving learned flashcards: {str(e)}")
            raise StorageException(
                f"Failed to retrieve learned flashcards: {str(e)}",
                operation="get_learned"
            )
