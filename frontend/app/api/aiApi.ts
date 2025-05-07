import { api, GrammarCheckResult, ChatMessage, EnhanceTextParams } from './index';

// Re-export the interfaces for backwards compatibility
export type { GrammarCheckResult, ChatMessage };

// Check grammar
export const checkGrammar = async (text: string): Promise<GrammarCheckResult> => {
  return api.language.checkGrammar(text);
};

// Enhance text (rewrite, paraphrase, or enhance)
export const enhanceText = async (text: string, task: 'rewrite' | 'paraphrase' | 'enhance'): Promise<string> => {
  return api.language.enhanceText({ text, task });
};

// Humanize AI-generated text
export const humanizeText = async (text: string): Promise<string> => {
  return api.language.humanizeText(text);
};

// Check AI probability
export const checkAIProbability = async (text: string): Promise<number> => {
  return api.language.checkAIProbability(text);
};

// Chat with AI
export const chatWithAI = async (messages: ChatMessage[]): Promise<string> => {
  return api.chat.sendMessage(messages);
}; 