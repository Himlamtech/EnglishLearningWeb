import React, { useState } from 'react';
import { Flashcard, api, FlashcardCreateParams } from '../app/api';
import FlashcardCard from '../app/components/FlashcardCard';
import { toast } from 'react-hot-toast';

const FlashcardGeneration: React.FC = () => {
  const [word, setWord] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('auto');
  const [flashcard, setFlashcard] = useState<Flashcard | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!word.trim()) {
      toast.error('Please enter a word');
      return;
    }

    // Validate word length
    if (word.trim().length > 100) {
      toast.error('Word must be no more than 100 characters long');
      return;
    }

    setLoading(true);
    try {
      const params: FlashcardCreateParams = { word: word.trim(), targetLanguage };
      const generated = await api.flashcard.generate(params);
      setFlashcard(generated);
      setWord(''); // Clear the input field on success
      toast.success('Flashcard generated successfully!');
    } catch (error: any) {
      console.error('Error generating flashcard:', error);

      // Handle specific error cases
      if (error.response?.status === 400) {
        const errorMessage = error.response?.data?.message || 'Invalid input';
        if (errorMessage.includes('already exists')) {
          toast.error(`Flashcard for "${word.trim()}" already exists`);
        } else if (errorMessage.includes('characters long')) {
          toast.error('Word must be no more than 100 characters long');
        } else {
          toast.error(errorMessage);
        }
      } else if (error.response?.status === 500) {
        toast.error('Server error. Please try again later.');
      } else {
        toast.error('Failed to generate flashcard. Please check your connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold gradient-text">Flashcard Generation</h1>
        <p className="mt-2 text-gray-600">
          Enter a word in English or Vietnamese to generate a translated flashcard
        </p>
      </div>

      <div className="card max-w-2xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="word" className="block text-sm font-medium text-gray-700 mb-1">
              Word
            </label>
            <input
              type="text"
              id="word"
              className="input-field"
              placeholder="Enter a word (e.g., apple, cây, happiness)"
              value={word}
              onChange={(e) => setWord(e.target.value)}
              maxLength={100}
              required
            />
          </div>

          <div>
            <label htmlFor="targetLanguage" className="block text-sm font-medium text-gray-700 mb-1">
              Target Language
            </label>
            <select
              id="targetLanguage"
              className="input-field"
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
            >
              <option value="auto">Auto Detect</option>
              <option value="en">English</option>
              <option value="vi">Vietnamese</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              * Auto will translate English to Vietnamese and Vietnamese to English
            </p>
          </div>

          <button
            type="submit"
            className="btn-primary w-full"
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Generate Flashcard'}
          </button>
        </form>
      </div>

      {/* Result Section */}
      {flashcard && (
        <div className="max-w-lg mx-auto">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Generated Flashcard</h2>
          <FlashcardCard flashcard={flashcard} />

          <div className="mt-8 text-center">
            <p className="text-sm text-gray-600 mb-4">
              Your flashcard has been saved automatically. You can view all your flashcards in the Learn section.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default FlashcardGeneration;