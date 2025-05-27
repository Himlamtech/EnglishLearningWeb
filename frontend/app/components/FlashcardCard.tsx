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
    <div className="card floating-card cursor-pointer h-64 transition-all duration-300 hover:shadow-2xl hover:scale-105 group" onClick={handleFlip}>
      {!flipped ? (
        /* Front side */
        <div className="h-full flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-blue-start/20 to-blue-end/20 rounded-bl-full"></div>
          <div className="text-center z-10">
            <h3 className="text-3xl font-bold bg-gradient-to-r from-blue-start to-blue-end bg-clip-text text-transparent group-hover:scale-110 transition-transform duration-300">
              {flashcard.word}
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mt-2 text-lg">{flashcard.pronunciation}</p>
          </div>

          <div className="mt-4 text-center">
            <div className="inline-flex items-center px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-full text-sm text-gray-600 dark:text-gray-300 group-hover:bg-primary/10 transition-colors duration-300">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Click to reveal
            </div>
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
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105 ${
                flashcard.isLearned
                  ? 'bg-gradient-to-r from-green-400 to-green-600 text-white shadow-lg shadow-green-500/25'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {loading ? (
                <div className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Loading...
                </div>
              ) : flashcard.isLearned ? (
                <div className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Learned
                </div>
              ) : (
                'Mark as Learned'
              )}
            </button>
          </div>
        </div>
      ) : (
        /* Back side */
        <div className="h-full flex flex-col justify-between relative overflow-hidden bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
          <div className="absolute top-0 left-0 w-20 h-20 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-br-full"></div>
          <div className="z-10">
            <div className="mb-4">
              <h4 className="text-xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent flex items-center">
                <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                </svg>
                Translation
              </h4>
              <p className="text-xl font-bold mt-2 text-gray-800 dark:text-gray-200">{flashcard.translatedWord}</p>
            </div>

            <div>
              <h4 className="text-xl font-semibold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent flex items-center">
                <svg className="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Synonyms
              </h4>
              <div className="mt-2 flex flex-wrap gap-2">
                {flashcard.synonyms.map((synonym, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 text-gray-700 dark:text-gray-300 rounded-full text-sm font-medium animate-fade-in-scale"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    {synonym}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="text-center">
            <div className="inline-flex items-center px-4 py-2 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-full text-sm text-gray-600 dark:text-gray-300">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Click to flip back
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FlashcardCard;