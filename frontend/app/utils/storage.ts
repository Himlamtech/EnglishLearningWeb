import { Flashcard } from './api';

// Storage keys
const FLASHCARDS_KEY = 'flashcards';

// Save flashcards to local storage
export const saveFlashcards = (flashcards: Flashcard[]): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(FLASHCARDS_KEY, JSON.stringify(flashcards));
  }
};

// Get flashcards from local storage
export const getFlashcards = (): Flashcard[] => {
  if (typeof window !== 'undefined') {
    const storedFlashcards = localStorage.getItem(FLASHCARDS_KEY);
    if (storedFlashcards) {
      return JSON.parse(storedFlashcards);
    }
  }
  return [];
};

// Add a new flashcard
export const addFlashcard = (flashcard: Flashcard): Flashcard[] => {
  const flashcards = getFlashcards();
  const updatedFlashcards = [...flashcards, flashcard];
  saveFlashcards(updatedFlashcards);
  return updatedFlashcards;
};

// Update a flashcard
export const updateFlashcard = (updatedFlashcard: Flashcard): Flashcard[] => {
  const flashcards = getFlashcards();
  const updatedFlashcards = flashcards.map(card => 
    card.word === updatedFlashcard.word ? updatedFlashcard : card
  );
  saveFlashcards(updatedFlashcards);
  return updatedFlashcards;
};

// Mark flashcard as learned
export const markAsLearned = (word: string, isLearned: boolean = true): Flashcard[] => {
  const flashcards = getFlashcards();
  const updatedFlashcards = flashcards.map(card => 
    card.word === word ? { ...card, isLearned } : card
  );
  saveFlashcards(updatedFlashcards);
  return updatedFlashcards;
};

// Export flashcards to CSV
export const exportToCSV = (): string => {
  const flashcards = getFlashcards();
  if (flashcards.length === 0) return '';
  
  // CSV header row
  const headers = ['Word', 'Translated Word', 'Pronunciation', 'Synonyms', 'Is Learned', 'Created At'];
  
  // Convert each flashcard to CSV row
  const rows = flashcards.map(card => [
    card.word,
    card.translatedWord,
    card.pronunciation,
    card.synonyms.join('; '),
    card.isLearned ? 'Yes' : 'No',
    card.createdAt
  ]);
  
  // Combine headers and rows
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');
  
  return csvContent;
};

// Import flashcards from CSV
export const importFromCSV = (csvContent: string): Flashcard[] => {
  const lines = csvContent.split('\n');
  if (lines.length <= 1) return [];
  
  // Skip header row
  const rows = lines.slice(1);
  
  // Parse each row into a flashcard
  const flashcards = rows.map(row => {
    const columns = row.split(',');
    // Remove quotes
    const cleanColumns = columns.map(col => col.replace(/^"|"$/g, ''));
    
    return {
      word: cleanColumns[0],
      translatedWord: cleanColumns[1],
      pronunciation: cleanColumns[2],
      synonyms: cleanColumns[3].split(';').map(s => s.trim()),
      isLearned: cleanColumns[4].toLowerCase() === 'yes',
      createdAt: cleanColumns[5] || new Date().toISOString()
    };
  });
  
  saveFlashcards([...getFlashcards(), ...flashcards]);
  return getFlashcards();
}; 