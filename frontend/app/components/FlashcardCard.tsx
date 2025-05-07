import React, { useState } from 'react';
import { Flashcard, FlashcardUpdateParams, api } from '../api';
import { toast } from 'react-hot-toast';

interface FlashcardCardProps {
  flashcard: Flashcard;
  onUpdate?: () => void;
}

const FlashcardCard: React.FC<FlashcardCardProps> = ({ flashcard, onUpdate }) => {
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedFlashcard, setEditedFlashcard] = useState<FlashcardUpdateParams>({
    word: flashcard.word,
    translatedWord: flashcard.translatedWord,
    pronunciation: flashcard.pronunciation,
    synonyms: flashcard.synonyms
  });

  const handleFlip = () => {
    if (!isEditing) {
      setFlipped(!flipped);
    }
  };

  const handleMarkLearned = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoading(true);

    try {
      await api.flashcard.markLearned(flashcard.word, !flashcard.isLearned);
      toast.success(`Flashcard marked as ${!flashcard.isLearned ? 'learned' : 'not learned'}`);
      if (onUpdate) {
        onUpdate();
      }
    } catch (error) {
      toast.error('Failed to update flashcard');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsEditing(true);
    setFlipped(false);
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(`Are you sure you want to delete the flashcard "${flashcard.word}"?`)) {
      setLoading(true);
      try {
        await api.flashcard.delete(flashcard.word);
        toast.success(`Flashcard "${flashcard.word}" deleted successfully`);
        if (onUpdate) {
          onUpdate();
        }
      } catch (error) {
        toast.error('Failed to delete flashcard');
        console.error(error);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.flashcard.update(flashcard.word, editedFlashcard);
      toast.success('Flashcard updated successfully');
      setIsEditing(false);
      if (onUpdate) {
        onUpdate();
      }
    } catch (error) {
      toast.error('Failed to update flashcard');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsEditing(false);
    setEditedFlashcard({
      word: flashcard.word,
      translatedWord: flashcard.translatedWord,
      pronunciation: flashcard.pronunciation,
      synonyms: flashcard.synonyms
    });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setEditedFlashcard(prev => ({
      ...prev,
      [name]: name === 'synonyms' ? value.split(',').map(s => s.trim()) : value
    }));
  };

  if (isEditing) {
    return (
      <div className="card h-auto p-4 border-2 border-primary-dark">
        <form onSubmit={handleSaveEdit}>
          <h3 className="text-xl font-bold text-primary-dark mb-4">Edit Flashcard</h3>

          <div className="mb-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Word</label>
            <input
              type="text"
              name="word"
              value={editedFlashcard.word}
              onChange={handleInputChange}
              className="w-full p-2 border rounded-md focus:ring-primary-dark focus:border-primary-dark"
              required
            />
          </div>

          <div className="mb-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Translation</label>
            <input
              type="text"
              name="translatedWord"
              value={editedFlashcard.translatedWord}
              onChange={handleInputChange}
              className="w-full p-2 border rounded-md focus:ring-primary-dark focus:border-primary-dark"
              required
            />
          </div>

          <div className="mb-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Pronunciation</label>
            <input
              type="text"
              name="pronunciation"
              value={editedFlashcard.pronunciation}
              onChange={handleInputChange}
              className="w-full p-2 border rounded-md focus:ring-primary-dark focus:border-primary-dark"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Synonyms (comma separated)</label>
            <input
              type="text"
              name="synonyms"
              value={editedFlashcard.synonyms?.join(', ')}
              onChange={handleInputChange}
              className="w-full p-2 border rounded-md focus:ring-primary-dark focus:border-primary-dark"
            />
          </div>

          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={handleCancelEdit}
              className="px-4 py-2 bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-primary-dark text-white rounded-md hover:bg-primary-darker transition-colors"
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div
      className={`card cursor-pointer h-64 perspective-1000 transition-transform duration-500 hover:shadow-lg ${flipped ? 'rotate-y-180' : ''}`}
      onClick={handleFlip}
    >
      <div className={`relative w-full h-full preserve-3d transition-all duration-500 ${flipped ? 'rotate-y-180' : ''}`}>
        {/* Front side */}
        <div className={`absolute w-full h-full backface-hidden ${flipped ? 'hidden' : 'block'}`}>
          <div className="p-4 h-full flex flex-col justify-between">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-primary-dark animate-fadeIn">{flashcard.word}</h3>
              <p className="text-gray-500 mt-2">{flashcard.pronunciation}</p>
            </div>

            <div className="mt-4 text-center">
              <p className="text-sm text-gray-600">Click to reveal translation and synonyms</p>
            </div>

            <div className="flex justify-between items-center mt-4">
              <div className="flex space-x-2">
                <button
                  onClick={handleEdit}
                  disabled={loading}
                  className="p-1 text-blue-600 hover:text-blue-800 transition-colors"
                  title="Edit flashcard"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  onClick={handleDelete}
                  disabled={loading}
                  className="p-1 text-red-600 hover:text-red-800 transition-colors"
                  title="Delete flashcard"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
              <button
                onClick={handleMarkLearned}
                disabled={loading}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  flashcard.isLearned
                    ? 'bg-green-100 text-green-800 hover:bg-green-200'
                    : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                }`}
              >
                {loading ? '...' : flashcard.isLearned ? 'Learned' : 'Mark as Learned'}
              </button>
            </div>
          </div>
        </div>

        {/* Back side */}
        <div className={`absolute w-full h-full backface-hidden rotate-y-180 ${flipped ? 'block' : 'hidden'}`}>
          <div className="p-4 h-full flex flex-col justify-between">
            <div>
              <h4 className="text-xl font-semibold text-primary-dark animate-fadeIn">Translation</h4>
              <p className="text-lg mt-1 animate-slideInRight">{flashcard.translatedWord}</p>

              <h4 className="text-xl font-semibold text-primary-dark mt-4 animate-fadeIn">Synonyms</h4>
              <ul className="mt-1 space-y-1">
                {flashcard.synonyms.map((synonym, index) => (
                  <li key={index} className="text-gray-700 animate-slideInRight" style={{ animationDelay: `${index * 100}ms` }}>{synonym}</li>
                ))}
              </ul>
            </div>

            <p className="text-sm text-gray-600 text-center">Click to flip back</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FlashcardCard;