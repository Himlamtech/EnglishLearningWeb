"""
Repository for flashcard data access operations.

This module provides a clean interface for all flashcard-related
database and file system operations with proper error handling.
"""

import os
import csv
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import Config
from utils.exceptions import StorageException, ValidationException
from utils.decorators import log_execution_time

logger = logging.getLogger(__name__)


class FlashcardRepository:
    """
    Repository for flashcard data access operations.

    Handles all CRUD operations for flashcards with proper error handling,
    validation, and logging.
    """

    def __init__(self, file_path: Optional[str] = None):
        """
        Initialize the flashcard repository.

        Args:
            file_path: Optional custom file path for flashcards storage
        """
        self.file_path = file_path or Config.FLASHCARDS_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure the flashcards CSV file exists with proper headers."""
        try:
            if not os.path.exists(self.file_path):
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

                # Create CSV with headers
                with open(self.file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['word', 'translatedWord', 'pronunciation', 'synonyms', 'isLearned', 'createdAt'])

                logger.info(f"Created new flashcards file: {self.file_path}")
        except Exception as e:
            raise StorageException(
                f"Failed to ensure flashcards file exists: {str(e)}",
                operation="file_creation",
                file_path=self.file_path
            )

    @log_execution_time(logger)
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all flashcards from storage.

        Returns:
            List of flashcard dictionaries

        Raises:
            StorageException: If reading fails
        """
        try:
            flashcards = []

            with open(self.file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row_num, row in enumerate(reader, start=2):  # Start at 2 because of header
                    try:
                        # Parse synonyms from string format
                        synonyms = row['synonyms'].split(';') if row['synonyms'] else []

                        flashcard = {
                            'word': row['word'],
                            'translatedWord': row['translatedWord'],
                            'pronunciation': row['pronunciation'],
                            'synonyms': synonyms,
                            'isLearned': row['isLearned'].lower() == 'true',
                            'createdAt': row['createdAt']
                        }

                        flashcards.append(flashcard)

                    except KeyError as e:
                        logger.warning(f"Missing field {e} in row {row_num}, skipping")
                        continue
                    except Exception as e:
                        logger.warning(f"Error parsing row {row_num}: {str(e)}, skipping")
                        continue

            logger.info(f"Successfully loaded {len(flashcards)} flashcards")
            return flashcards

        except FileNotFoundError:
            logger.info("Flashcards file not found, returning empty list")
            return []
        except Exception as e:
            raise StorageException(
                f"Failed to read flashcards: {str(e)}",
                operation="read",
                file_path=self.file_path
            )

    @log_execution_time(logger)
    def add(self, flashcard_data: Dict[str, Any]) -> bool:
        """
        Add a new flashcard to storage.

        Args:
            flashcard_data: Flashcard data dictionary

        Returns:
            True if successful

        Raises:
            StorageException: If adding fails
            ValidationException: If data is invalid
        """
        try:
            # Validate required fields
            required_fields = ['word', 'translatedWord', 'pronunciation', 'synonyms']
            for field in required_fields:
                if field not in flashcard_data:
                    raise ValidationException(
                        f"Missing required field: {field}",
                        field=field
                    )

            # Add metadata if not present
            if 'createdAt' not in flashcard_data:
                flashcard_data['createdAt'] = datetime.now().isoformat()

            if 'isLearned' not in flashcard_data:
                flashcard_data['isLearned'] = False

            # Convert synonyms list to string
            synonyms_str = ';'.join(flashcard_data['synonyms']) if flashcard_data['synonyms'] else ''

            # Prepare row data
            row_data = {
                'word': flashcard_data['word'],
                'translatedWord': flashcard_data['translatedWord'],
                'pronunciation': flashcard_data['pronunciation'],
                'synonyms': synonyms_str,
                'isLearned': str(flashcard_data['isLearned']).lower(),
                'createdAt': flashcard_data['createdAt']
            }

            # Check if file exists and has content
            file_exists = os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0

            with open(self.file_path, mode='a' if file_exists else 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['word', 'translatedWord', 'pronunciation', 'synonyms', 'isLearned', 'createdAt']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                # Write header if creating a new file
                if not file_exists:
                    writer.writeheader()

                # Write the row
                writer.writerow(row_data)

            logger.info(f"Successfully added flashcard: {flashcard_data['word']}")
            return True

        except (ValidationException, StorageException):
            raise
        except Exception as e:
            raise StorageException(
                f"Failed to add flashcard: {str(e)}",
                operation="add",
                file_path=self.file_path
            )

    @log_execution_time(logger)
    def update(self, word: str, updated_data: Dict[str, Any]) -> bool:
        """
        Update an existing flashcard.

        Args:
            word: Word to identify the flashcard
            updated_data: Data to update

        Returns:
            True if successful, False if not found

        Raises:
            StorageException: If update fails
        """
        try:
            # Read existing data
            flashcards = self.get_all()

            # Find the flashcard to update
            found = False
            for i, flashcard in enumerate(flashcards):
                if flashcard['word'] == word:
                    found = True

                    # Update fields
                    for key, value in updated_data.items():
                        if key in flashcard:
                            flashcard[key] = value

                    flashcards[i] = flashcard
                    break

            if not found:
                logger.warning(f"Flashcard with word '{word}' not found for update")
                return False

            # Write all flashcards back to file
            self._write_all_flashcards(flashcards)

            logger.info(f"Successfully updated flashcard: {word}")
            return True

        except StorageException:
            raise
        except Exception as e:
            raise StorageException(
                f"Failed to update flashcard '{word}': {str(e)}",
                operation="update",
                file_path=self.file_path
            )

    @log_execution_time(logger)
    def delete(self, word: str) -> bool:
        """
        Delete a flashcard by word.

        Args:
            word: Word to identify the flashcard to delete

        Returns:
            True if successful, False if not found

        Raises:
            StorageException: If deletion fails
        """
        try:
            # Read existing data
            flashcards = self.get_all()

            # Filter out the flashcard to delete
            original_count = len(flashcards)
            flashcards = [f for f in flashcards if f['word'] != word]

            # Check if any flashcard was removed
            if len(flashcards) == original_count:
                logger.warning(f"Flashcard with word '{word}' not found for deletion")
                return False

            # Write remaining flashcards back to file
            self._write_all_flashcards(flashcards)

            logger.info(f"Successfully deleted flashcard: {word}")
            return True

        except StorageException:
            raise
        except Exception as e:
            raise StorageException(
                f"Failed to delete flashcard '{word}': {str(e)}",
                operation="delete",
                file_path=self.file_path
            )

    def _write_all_flashcards(self, flashcards: List[Dict[str, Any]]) -> None:
        """
        Write all flashcards to the CSV file.

        Args:
            flashcards: List of flashcard dictionaries

        Raises:
            StorageException: If writing fails
        """
        try:
            with open(self.file_path, mode='w', newline='', encoding='utf-8') as file:
                fieldnames = ['word', 'translatedWord', 'pronunciation', 'synonyms', 'isLearned', 'createdAt']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                for flashcard in flashcards:
                    # Convert synonyms list to string
                    synonyms_str = ';'.join(flashcard['synonyms']) if flashcard['synonyms'] else ''

                    writer.writerow({
                        'word': flashcard['word'],
                        'translatedWord': flashcard['translatedWord'],
                        'pronunciation': flashcard['pronunciation'],
                        'synonyms': synonyms_str,
                        'isLearned': str(flashcard['isLearned']).lower(),
                        'createdAt': flashcard['createdAt']
                    })

        except Exception as e:
            raise StorageException(
                f"Failed to write flashcards to file: {str(e)}",
                operation="write",
                file_path=self.file_path
            )

    @log_execution_time(logger)
    def mark_as_learned(self, word: str, is_learned: bool = True) -> bool:
        """
        Mark a flashcard as learned or not learned.

        Args:
            word: Word to identify the flashcard
            is_learned: Whether the flashcard is learned

        Returns:
            True if successful, False if not found

        Raises:
            StorageException: If update fails
        """
        return self.update(word, {'isLearned': is_learned})

    @log_execution_time(logger)
    def export_to_json(self) -> str:
        """
        Export all flashcards to JSON format.

        Returns:
            JSON string containing all flashcards

        Raises:
            StorageException: If export fails
        """
        try:
            flashcards = self.get_all()
            json_data = json.dumps(flashcards, indent=2, ensure_ascii=False)
            logger.info(f"Successfully exported {len(flashcards)} flashcards to JSON")
            return json_data

        except StorageException:
            raise
        except Exception as e:
            raise StorageException(
                f"Failed to export flashcards to JSON: {str(e)}",
                operation="export",
                file_path=self.file_path
            )

    @log_execution_time(logger)
    def import_from_csv(self, csv_content: str) -> bool:
        """
        Import flashcards from CSV content.

        Args:
            csv_content: CSV content as string

        Returns:
            True if successful

        Raises:
            StorageException: If import fails
            ValidationException: If CSV format is invalid
        """
        try:
            # Create a temporary file to process the CSV content
            temp_file = f"{self.file_path}.temp"

            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(csv_content)

                # Read and validate the temp file
                with open(temp_file, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)

                    # Check for required columns
                    if not reader.fieldnames:
                        raise ValidationException(
                            "CSV file is empty or has no headers",
                            field="csv_headers"
                        )

                    required_columns = ['word', 'translatedWord', 'pronunciation', 'synonyms']
                    missing_columns = [col for col in required_columns if col not in reader.fieldnames]

                    if missing_columns:
                        raise ValidationException(
                            f"CSV is missing required columns: {', '.join(missing_columns)}",
                            field="csv_columns",
                            value=missing_columns
                        )

                    # Process and add each flashcard
                    imported_count = 0
                    for row_num, row in enumerate(reader, start=2):
                        try:
                            synonyms = row['synonyms'].split(';') if row['synonyms'] else []

                            flashcard = {
                                'word': row['word'].strip(),
                                'translatedWord': row['translatedWord'].strip(),
                                'pronunciation': row['pronunciation'].strip(),
                                'synonyms': [s.strip() for s in synonyms if s.strip()],
                                'isLearned': row.get('isLearned', 'false').lower() == 'true',
                                'createdAt': row.get('createdAt', datetime.now().isoformat())
                            }

                            # Validate that word is not empty
                            if not flashcard['word']:
                                logger.warning(f"Skipping row {row_num}: empty word")
                                continue

                            self.add(flashcard)
                            imported_count += 1

                        except Exception as e:
                            logger.warning(f"Error importing row {row_num}: {str(e)}, skipping")
                            continue

                logger.info(f"Successfully imported {imported_count} flashcards from CSV")
                return True

            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.remove(temp_file)

        except (ValidationException, StorageException):
            raise
        except Exception as e:
            raise StorageException(
                f"Failed to import flashcards from CSV: {str(e)}",
                operation="import",
                file_path=self.file_path
            )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the flashcard collection.

        Returns:
            Dictionary containing statistics

        Raises:
            StorageException: If reading fails
        """
        try:
            flashcards = self.get_all()

            total_count = len(flashcards)
            learned_count = sum(1 for f in flashcards if f['isLearned'])
            unlearned_count = total_count - learned_count

            # Calculate learning progress percentage
            progress_percentage = (learned_count / total_count * 100) if total_count > 0 else 0

            # Get creation date range
            creation_dates = [f['createdAt'] for f in flashcards if f['createdAt']]
            earliest_date = min(creation_dates) if creation_dates else None
            latest_date = max(creation_dates) if creation_dates else None

            statistics = {
                'total_flashcards': total_count,
                'learned_flashcards': learned_count,
                'unlearned_flashcards': unlearned_count,
                'learning_progress_percentage': round(progress_percentage, 1),
                'earliest_creation_date': earliest_date,
                'latest_creation_date': latest_date
            }

            logger.info(f"Generated statistics for {total_count} flashcards")
            return statistics

        except StorageException:
            raise
        except Exception as e:
            raise StorageException(
                f"Failed to generate statistics: {str(e)}",
                operation="statistics",
                file_path=self.file_path
            )

    def find_by_word(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Find a flashcard by its word.

        Args:
            word: Word to search for

        Returns:
            Flashcard dictionary if found, None otherwise

        Raises:
            StorageException: If search fails
        """
        try:
            flashcards = self.get_all()

            for flashcard in flashcards:
                if flashcard['word'].lower() == word.lower():
                    return flashcard

            return None

        except StorageException:
            raise
        except Exception as e:
            raise StorageException(
                f"Failed to find flashcard by word '{word}': {str(e)}",
                operation="find",
                file_path=self.file_path
            )
