import React, { useEffect, useState } from 'react';
import { Flashcard, api } from '../app/api';
import FlashcardCard from '../app/components/FlashcardCard';
import { toast } from 'react-hot-toast';

const LearnFlashcard: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'learned' | 'not-learned'>('all');

  useEffect(() => {
    fetchFlashcards();
  }, []);

  const fetchFlashcards = async () => {
    setLoading(true);
    try {
      const data = await api.flashcard.getAll();
      setFlashcards(data);
    } catch (error) {
      console.error('Failed to fetch flashcards:', error);
      toast.error('Failed to load flashcards');
    } finally {
      setLoading(false);
    }
  };

  const filteredFlashcards = () => {
    switch (filter) {
      case 'learned':
        return flashcards.filter(card => card.isLearned);
      case 'not-learned':
        return flashcards.filter(card => !card.isLearned);
      default:
        return flashcards;
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold gradient-text">Learn Flashcards</h1>
        <p className="mt-2 text-gray-600">
          Review and practice your flashcards
        </p>
      </div>

      {/* Filter Controls */}
      <div className="flex justify-center space-x-4">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-md ${
            filter === 'all'
              ? 'bg-primary-dark text-white'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilter('learned')}
          className={`px-4 py-2 rounded-md ${
            filter === 'learned'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          }`}
        >
          Learned
        </button>
        <button
          onClick={() => setFilter('not-learned')}
          className={`px-4 py-2 rounded-md ${
            filter === 'not-learned'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          }`}
        >
          Not Learned
        </button>
      </div>

      {/* Flashcards Grid */}
      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Loading flashcards...</p>
        </div>
      ) : filteredFlashcards().length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredFlashcards().map((flashcard) => (
            <FlashcardCard
              key={flashcard.word}
              flashcard={flashcard}
              onUpdate={fetchFlashcards}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500">No flashcards found.</p>
          <a href="/flashcard-generation" className="btn-primary inline-block mt-4">
            Create Your First Flashcard
          </a>
        </div>
      )}
    </div>
  );
};

export default LearnFlashcard;
