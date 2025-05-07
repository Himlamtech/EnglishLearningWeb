import axios from 'axios';

// API base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create an axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interfaces
export interface Flashcard {
  word: string;
  translatedWord: string;
  pronunciation: string;
  synonyms: string[];
  isLearned: boolean;
}

export interface FlashcardCreateParams {
  word: string;
  targetLanguage?: string;
}

export interface FlashcardUpdateParams {
  word?: string;
  translatedWord?: string;
  pronunciation?: string;
  synonyms?: string[];
  isLearned?: boolean;
}

export interface GrammarCheckResult {
  correctedText: string;
  errors: string[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface EnhanceTextParams {
  text: string;
  task: 'rewrite' | 'paraphrase' | 'enhance';
}

// Flashcard API
const flashcardApi = {
  // Generate a flashcard
  generate: async (params: FlashcardCreateParams): Promise<Flashcard> => {
    try {
      const { word, targetLanguage = 'auto' } = params;
      const response = await apiClient.post('/flashcards', { word, targetLanguage });
      return response.data;
    } catch (error) {
      console.error('Error generating flashcard:', error);
      throw error;
    }
  },

  // Get all flashcards
  getAll: async (): Promise<Flashcard[]> => {
    try {
      const response = await apiClient.get('/flashcards');
      return response.data;
    } catch (error) {
      console.error('Error fetching flashcards:', error);
      throw error;
    }
  },

  // Mark a flashcard as learned/not learned
  markLearned: async (word: string, isLearned: boolean = true): Promise<boolean> => {
    try {
      await apiClient.put(`/flashcards/${encodeURIComponent(word)}/learned?is_learned=${isLearned}`);
      return true;
    } catch (error) {
      console.error('Error marking flashcard:', error);
      throw error;
    }
  },

  // Update a flashcard
  update: async (word: string, params: FlashcardUpdateParams): Promise<Flashcard> => {
    try {
      const response = await apiClient.put(`/flashcards/${encodeURIComponent(word)}`, params);
      return response.data;
    } catch (error) {
      console.error('Error updating flashcard:', error);
      throw error;
    }
  },

  // Delete a flashcard
  delete: async (word: string): Promise<boolean> => {
    try {
      await apiClient.delete(`/flashcards/${encodeURIComponent(word)}`);
      return true;
    } catch (error) {
      console.error('Error deleting flashcard:', error);
      throw error;
    }
  },

  // Export flashcards
  export: async (): Promise<string> => {
    try {
      const response = await apiClient.get('/flashcards/export');
      return response.data.data;
    } catch (error) {
      console.error('Error exporting flashcards:', error);
      throw error;
    }
  },

  // Import flashcards
  import: async (csvContent: string): Promise<boolean> => {
    try {
      await apiClient.post('/flashcards/import', { text: csvContent });
      return true;
    } catch (error) {
      console.error('Error importing flashcards:', error);
      throw error;
    }
  }
};

// Language & Writing API
const languageApi = {
  // Check grammar
  checkGrammar: async (text: string): Promise<GrammarCheckResult> => {
    try {
      const response = await apiClient.post('/grammar-check', { text });
      return response.data;
    } catch (error) {
      console.error('Error checking grammar:', error);
      throw error;
    }
  },

  // Enhance text (rewrite, paraphrase, or enhance)
  enhanceText: async (params: EnhanceTextParams): Promise<string> => {
    try {
      const { text, task } = params;
      const response = await apiClient.post('/enhance-text', { text, task });
      return response.data.enhancedText;
    } catch (error) {
      console.error('Error enhancing text:', error);
      throw error;
    }
  },

  // Humanize AI-generated text
  humanizeText: async (text: string): Promise<string> => {
    try {
      const response = await apiClient.post('/humanize-text', { text });
      return response.data.humanizedText;
    } catch (error) {
      console.error('Error humanizing text:', error);
      throw error;
    }
  },

  // Check AI probability
  checkAIProbability: async (text: string): Promise<number> => {
    try {
      const response = await apiClient.post('/ai-probability', { text });
      return response.data.probability;
    } catch (error) {
      console.error('Error checking AI probability:', error);
      throw error;
    }
  }
};

// Chat API
const chatApi = {
  // Chat with AI
  sendMessage: async (messages: ChatMessage[]): Promise<string> => {
    try {
      const response = await apiClient.post('/chat', { messages });
      return response.data.response;
    } catch (error) {
      console.error('Error chatting with AI:', error);
      throw error;
    }
  }
};

// Health check
const healthApi = {
  check: async (): Promise<boolean> => {
    try {
      const response = await apiClient.get('/health');
      return response.data.status === 'ok';
    } catch (error) {
      console.error('API health check failed:', error);
      return false;
    }
  }
};

// Export unified API object
export const api = {
  flashcard: flashcardApi,
  language: languageApi,
  chat: chatApi,
  health: healthApi
};

export default api;