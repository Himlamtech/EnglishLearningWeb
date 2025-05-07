import { api, Flashcard, FlashcardCreateParams } from './index';

// Re-export the Flashcard type for backwards compatibility
export type { Flashcard };

// Generate a flashcard
export const generateFlashcard = async (word: string, targetLanguage: string = 'auto'): Promise<Flashcard> => {
  return api.flashcard.generate({ word, targetLanguage });
};

// Get all flashcards
export const getFlashcards = async (): Promise<Flashcard[]> => {
  return api.flashcard.getAll();
};

// Mark a flashcard as learned/not learned
export const markFlashcardLearned = async (word: string, isLearned: boolean = true): Promise<boolean> => {
  return api.flashcard.markLearned(word, isLearned);
};

// Export flashcards
export const exportFlashcards = async (): Promise<string> => {
  return api.flashcard.export();
};

// Import flashcards
export const importFlashcards = async (csvContent: string): Promise<boolean> => {
  return api.flashcard.import(csvContent);
}; 