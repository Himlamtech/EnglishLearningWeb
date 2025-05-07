import axios from 'axios';

// Define API base URL from environment variable or default to YesScale API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://api.yescale.io';
const API_KEY = process.env.NEXT_PUBLIC_OPENAI_API_KEY;

// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`,
  },
});

// Define the flashcard type
export interface Flashcard {
  word: string;
  translatedWord: string;
  pronunciation: string;
  synonyms: string[];
  isLearned: boolean;
  createdAt: string;
}

// Function to generate flashcard using OpenAI function calling
export async function generateFlashcard(word: string, targetLanguage: string = 'auto'): Promise<Flashcard> {
  const response = await apiClient.post('/v1/chat/completions', {
    model: 'gpt-4.1-nano-2025-04-14',
    messages: [
      {
        role: 'system',
        content: 'You are a helpful language learning assistant that generates flashcards with precise information.'
      },
      {
        role: 'user',
        content: `Create a flashcard for the word: "${word}". If the word is in English, translate to Vietnamese. If the word is in Vietnamese, translate to English.`
      }
    ],
    functions: [
      {
        name: 'create_flashcard',
        description: 'Create a language learning flashcard',
        parameters: {
          type: 'object',
          properties: {
            word: {
              type: 'string',
              description: 'The original word'
            },
            translatedWord: {
              type: 'string',
              description: 'Translation of the word'
            },
            pronunciation: {
              type: 'string',
              description: 'Pronunciation guide for the word'
            },
            synonyms: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: '3 synonyms of the word'
            }
          },
          required: ['word', 'translatedWord', 'pronunciation', 'synonyms']
        }
      }
    ],
    function_call: { name: 'create_flashcard' }
  });

  const functionCall = response.data.choices[0].message.function_call;
  const functionArgs = JSON.parse(functionCall.arguments);

  return {
    ...functionArgs,
    isLearned: false,
    createdAt: new Date().toISOString()
  };
}

// Function to check grammar
export async function checkGrammar(text: string): Promise<{correctedText: string; errors: string[]}> {
  const response = await apiClient.post('/v1/chat/completions', {
    model: 'gpt-4.1-nano-2025-04-14',
    messages: [
      {
        role: 'system',
        content: 'You are a helpful grammar assistant that corrects text and identifies grammar errors.'
      },
      {
        role: 'user',
        content: `Check the grammar in this text: "${text}"`
      }
    ],
    functions: [
      {
        name: 'grammar_check',
        description: 'Check and correct grammar in text',
        parameters: {
          type: 'object',
          properties: {
            correctedText: {
              type: 'string',
              description: 'The corrected text with proper grammar'
            },
            errors: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'List of identified grammar errors'
            }
          },
          required: ['correctedText', 'errors']
        }
      }
    ],
    function_call: { name: 'grammar_check' }
  });

  const functionCall = response.data.choices[0].message.function_call;
  return JSON.parse(functionCall.arguments);
}

// Function to enhance writing
export async function enhanceWriting(text: string, task: 'rewrite' | 'paraphrase' | 'enhance'): Promise<string> {
  const promptMap = {
    rewrite: 'Rewrite this text to improve clarity and flow:',
    paraphrase: 'Paraphrase this text while preserving its meaning:',
    enhance: 'Enhance this writing to make it more engaging and professional:'
  };

  const response = await apiClient.post('/v1/chat/completions', {
    model: 'gpt-4.1-nano-2025-04-14',
    messages: [
      {
        role: 'system',
        content: 'You are a professional writing assistant that helps improve text.'
      },
      {
        role: 'user',
        content: `${promptMap[task]} "${text}"`
      }
    ]
  });

  return response.data.choices[0].message.content;
}

// Function to humanize AI text
export async function humanizeText(text: string): Promise<string> {
  const response = await apiClient.post('/v1/chat/completions', {
    model: 'gpt-4.1-nano-2025-04-14',
    messages: [
      {
        role: 'system',
        content: 'You are an assistant that makes AI-generated text sound more natural and human-like.'
      },
      {
        role: 'user',
        content: `Make this text sound more natural and human-like: "${text}"`
      }
    ]
  });

  return response.data.choices[0].message.content;
}

// Function to check AI probability
export async function checkAIProbability(text: string): Promise<number> {
  // Note: This is a simplified implementation
  // In a real application, you would use a specialized AI detection API
  const response = await apiClient.post('/v1/chat/completions', {
    model: 'gpt-4.1-nano-2025-04-14',
    messages: [
      {
        role: 'system',
        content: 'You are an assistant that analyzes text to determine the probability it was generated by AI.'
      },
      {
        role: 'user',
        content: `On a scale from 0 to 100, what is the probability that this text was generated by AI? Only respond with a number. Text: "${text}"`
      }
    ]
  });

  const content = response.data.choices[0].message.content;
  // Extract just the number from the response
  const probability = parseInt(content.match(/\d+/)[0]);
  return Math.min(100, Math.max(0, probability)); // Ensure the result is between 0 and 100
}

// Chat with AI
export async function chatWithAI(messages: Array<{role: string, content: string}>): Promise<string> {
  const response = await apiClient.post('/v1/chat/completions', {
    model: 'gpt-4.1-nano-2025-04-14',
    messages: [
      {
        role: 'system',
        content: 'You are a helpful language learning assistant. You provide concise, accurate responses to help users learn languages. You can explain grammar concepts, vocabulary, idioms, and cultural context.'
      },
      ...messages
    ]
  });

  return response.data.choices[0].message.content;
}

export default apiClient; 