import React, { useState } from 'react';
import { api, GrammarCheckResult } from '../app/api';
import { toast } from 'react-hot-toast';

const GrammarChecking: React.FC = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState<GrammarCheckResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) {
      toast.error('Please enter some text');
      return;
    }

    setLoading(true);
    try {
      const checkResult = await api.language.checkGrammar(text);
      setResult(checkResult);
    } catch (error) {
      console.error('Error checking grammar:', error);
      toast.error('Failed to check grammar');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = () => {
    if (result) {
      navigator.clipboard.writeText(result.correctedText);
      toast.success('Corrected text copied to clipboard');
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold gradient-text">Grammar Checking</h1>
        <p className="mt-2 text-gray-600">
          Check and correct grammar in your writing
        </p>
      </div>

      <div className="card max-w-3xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="text" className="block text-sm font-medium text-gray-700 mb-1">
              Your Text
            </label>
            <textarea
              id="text"
              rows={6}
              className="input-field"
              placeholder="Enter text to check grammar (e.g., She have a cat. Their is a problem with this sentence.)"
              value={text}
              onChange={(e) => setText(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn-primary w-full"
            disabled={loading}
          >
            {loading ? 'Checking...' : 'Check Grammar'}
          </button>
        </form>
      </div>

      {/* Results Section */}
      {result && (
        <div className="card max-w-3xl mx-auto">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">Results</h2>
            <button
              onClick={handleCopyText}
              className="text-primary-dark hover:text-primary-light text-sm flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
              </svg>
              Copy Corrected Text
            </button>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Corrected Text</h3>
            <div className="p-4 bg-gray-50 rounded-md">
              <p className="whitespace-pre-wrap">{result.correctedText}</p>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Grammar Issues</h3>
            {result.errors.length > 0 && result.errors[0] !== 'No grammar errors found' ? (
              <ul className="list-disc pl-5 space-y-1">
                {result.errors.map((error, index) => (
                  <li key={index} className="text-red-600">{error}</li>
                ))}
              </ul>
            ) : (
              <p className="text-green-600">No grammar errors found!</p>
            )}
          </div>
        </div>
      )}

      <div className="max-w-3xl mx-auto">
        <h2 className="text-xl font-semibold text-gray-800 mb-2">Example Sentences to Try</h2>
        <div className="grid grid-cols-1 gap-2">
          <button
            onClick={() => setText("She have a cat. Their is a problem with this sentence.")}
            className="text-left p-2 bg-gray-100 hover:bg-gray-200 rounded"
          >
            "She have a cat. Their is a problem with this sentence."
          </button>
          <button
            onClick={() => setText("I goed to the store yesterday and buyed some milk.")}
            className="text-left p-2 bg-gray-100 hover:bg-gray-200 rounded"
          >
            "I goed to the store yesterday and buyed some milk."
          </button>
          <button
            onClick={() => setText("The childrens are playing in the park with they toys.")}
            className="text-left p-2 bg-gray-100 hover:bg-gray-200 rounded"
          >
            "The childrens are playing in the park with they toys."
          </button>
        </div>
      </div>
    </div>
  );
};

export default GrammarChecking;
