import React, { useState } from 'react';
import { Flashcard, api } from '../api';
import { toast } from 'react-hot-toast';

interface FlashcardCardProps {
  flashcard: Flashcard;
  onUpdate?: () => void;
}

const FlashcardCard: React.FC<FlashcardCardProps> = ({ flashcard, onUpdate }) => {
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleFlip = () => {
    setFlipped(!flipped);
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

  return (
    <div 
      className={`card cursor-pointer h-64 perspective-1000 transition-transform duration-500 ${flipped ? 'rotate-y-180' : ''}`}
      onClick={handleFlip}
    >
      <div className={`relative w-full h-full preserve-3d transition-all duration-500 ${flipped ? 'rotate-y-180' : ''}`}>
        {/* Front side */}
        <div className={`absolute w-full h-full backface-hidden ${flipped ? 'hidden' : 'block'}`}>
          <div className="p-4 h-full flex flex-col justify-between">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-primary-dark">{flashcard.word}</h3>
              <p className="text-gray-500 mt-2">{flashcard.pronunciation}</p>
            </div>
            
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-600">Click to reveal translation and synonyms</p>
            </div>
            
            <div className="flex justify-between items-center mt-4">
              <span className="text-xs text-gray-400">
                {(flashcard as any).createdAt ? new Date((flashcard as any).createdAt).toLocaleDateString() : ''}
              </span>
              <button
                onClick={handleMarkLearned}
                disabled={loading}
                className={`px-3 py-1 rounded-md text-sm font-medium ${
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
              <h4 className="text-xl font-semibold text-primary-dark">Translation</h4>
              <p className="text-lg mt-1">{flashcard.translatedWord}</p>
              
              <h4 className="text-xl font-semibold text-primary-dark mt-4">Synonyms</h4>
              <ul className="mt-1 space-y-1">
                {flashcard.synonyms.map((synonym, index) => (
                  <li key={index} className="text-gray-700">{synonym}</li>
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