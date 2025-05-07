import os
import csv
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import FLASHCARDS_FILE
from models import Flashcard

def ensure_file_exists():
    """Ensure the flashcards CSV file exists with headers."""
    if not os.path.exists(FLASHCARDS_FILE):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(FLASHCARDS_FILE), exist_ok=True)

        # Create CSV with headers
        with open(FLASHCARDS_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['word', 'translatedWord', 'pronunciation', 'synonyms', 'isLearned', 'createdAt'])

def get_flashcards() -> List[Dict[str, Any]]:
    """Get all flashcards from the CSV file."""
    ensure_file_exists()

    try:
        flashcards = []
        with open(FLASHCARDS_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
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

        return flashcards
    except Exception as e:
        print(f"Error reading flashcards: {e}")
        return []

def add_flashcard(flashcard: Dict[str, Any]) -> bool:
    """Add a new flashcard to the CSV file."""
    ensure_file_exists()

    try:
        # Add created time if not present
        if 'createdAt' not in flashcard:
            flashcard['createdAt'] = datetime.now().isoformat()

        # Set isLearned to False if not present
        if 'isLearned' not in flashcard:
            flashcard['isLearned'] = False

        # Convert synonyms list to string
        synonyms_str = ';'.join(flashcard['synonyms']) if flashcard['synonyms'] else ''

        # Prepare row data
        row_data = {
            'word': flashcard['word'],
            'translatedWord': flashcard['translatedWord'],
            'pronunciation': flashcard['pronunciation'],
            'synonyms': synonyms_str,
            'isLearned': str(flashcard['isLearned']).lower(),
            'createdAt': flashcard['createdAt']
        }

        # Check if file exists and has content
        file_exists = os.path.exists(FLASHCARDS_FILE) and os.path.getsize(FLASHCARDS_FILE) > 0

        with open(FLASHCARDS_FILE, mode='a' if file_exists else 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['word', 'translatedWord', 'pronunciation', 'synonyms', 'isLearned', 'createdAt']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Write header if creating a new file
            if not file_exists:
                writer.writeheader()

            # Write the row
            writer.writerow(row_data)

        return True
    except Exception as e:
        print(f"Error adding flashcard: {e}")
        return False

def update_flashcard(word: str, updated_data: Dict[str, Any]) -> bool:
    """Update an existing flashcard in the CSV file."""
    ensure_file_exists()

    try:
        # Read existing data
        flashcards = get_flashcards()

        # Find the flashcard to update
        found = False
        for i, flashcard in enumerate(flashcards):
            if flashcard['word'] == word:
                found = True
                # Update fields
                if 'translatedWord' in updated_data:
                    flashcard['translatedWord'] = updated_data['translatedWord']
                if 'pronunciation' in updated_data:
                    flashcard['pronunciation'] = updated_data['pronunciation']
                if 'synonyms' in updated_data:
                    flashcard['synonyms'] = updated_data['synonyms']
                if 'isLearned' in updated_data:
                    flashcard['isLearned'] = updated_data['isLearned']
                flashcards[i] = flashcard
                break

        if not found:
            return False  # Flashcard not found

        # Write all flashcards back to file
        with open(FLASHCARDS_FILE, mode='w', newline='', encoding='utf-8') as file:
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

        return True
    except Exception as e:
        print(f"Error updating flashcard: {e}")
        return False

def mark_as_learned(word: str, is_learned: bool = True) -> bool:
    """Mark a flashcard as learned or not learned."""
    return update_flashcard(word, {'isLearned': is_learned})

def export_to_json() -> str:
    """Export flashcards to JSON format."""
    flashcards = get_flashcards()
    return json.dumps(flashcards, indent=2)

def import_from_csv(csv_content: str) -> bool:
    """Import flashcards from CSV content."""
    try:
        # Create a temporary file
        temp_file = 'temp_import.csv'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        # Read the temp file
        with open(temp_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Check for required columns
            if not reader.fieldnames:
                os.remove(temp_file)
                return False

            required_columns = ['word', 'translatedWord', 'pronunciation', 'synonyms']
            if not all(col in reader.fieldnames for col in required_columns):
                os.remove(temp_file)
                return False

            # Process and add each flashcard
            for row in reader:
                synonyms = row['synonyms'].split(';') if row['synonyms'] else []

                flashcard = {
                    'word': row['word'],
                    'translatedWord': row['translatedWord'],
                    'pronunciation': row['pronunciation'],
                    'synonyms': synonyms,
                    'isLearned': row.get('isLearned', 'false').lower() == 'true',
                    'createdAt': row.get('createdAt', datetime.now().isoformat())
                }

                add_flashcard(flashcard)

        # Clean up
        os.remove(temp_file)
        return True
    except Exception as e:
        print(f"Error importing flashcards: {e}")
        return False