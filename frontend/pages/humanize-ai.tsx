import React, { useState } from 'react';
import { api } from '../app/api';
import { toast } from 'react-hot-toast';

const HumanizeAI: React.FC = () => {
  const [text, setText] = useState('');
  const [humanizedText, setHumanizedText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) {
      toast.error('Please enter some text');
      return;
    }

    setLoading(true);
    try {
      const result = await api.language.humanizeText(text);
      setHumanizedText(result);
    } catch (error) {
      console.error('Error humanizing text:', error);
      toast.error('Failed to humanize text');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = () => {
    if (humanizedText) {
      navigator.clipboard.writeText(humanizedText);
      toast.success('Humanized text copied to clipboard');
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold gradient-text">Humanize AI Text</h1>
        <p className="mt-2 text-gray-600">
          Make AI-generated text sound more natural and human-like
        </p>
      </div>

      <div className="card max-w-3xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="text" className="block text-sm font-medium text-gray-700 mb-1">
              AI-Generated Text
            </label>
            <textarea
              id="text"
              rows={6}
              className="input-field"
              placeholder="Paste AI-generated text here to make it sound more natural..."
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
            {loading ? 'Humanizing...' : 'Humanize Text'}
          </button>
        </form>
      </div>

      {/* Results Section */}
      {humanizedText && (
        <div className="card max-w-3xl mx-auto">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">Humanized Result</h2>
            <button
              onClick={handleCopyText}
              className="text-primary-dark hover:text-primary-light text-sm flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
              </svg>
              Copy Text
            </button>
          </div>

          <div className="p-4 bg-gray-50 rounded-md">
            <p className="whitespace-pre-wrap">{humanizedText}</p>
          </div>
        </div>
      )}

      <div className="max-w-3xl mx-auto">
        <h2 className="text-xl font-semibold text-gray-800 mb-2">Example AI Text to Try</h2>
        <div className="grid grid-cols-1 gap-2">
          <button
            onClick={() => setText("The utilization of artificial intelligence in educational contexts has demonstrated significant efficacy in enhancing learning outcomes across diverse student populations. Implementation of such technologies facilitates personalized learning experiences tailored to individual cognitive profiles, thereby optimizing knowledge acquisition and retention rates.")}
            className="text-left p-2 bg-gray-100 hover:bg-gray-200 rounded"
          >
            Formal AI-generated text
          </button>
          <button
            onClick={() => setText("Language learning is a process that requires consistent practice and exposure to the target language. Vocabulary acquisition, grammatical understanding, and pronunciation skills are fundamental components that must be developed simultaneously for optimal proficiency development.")}
            className="text-left p-2 bg-gray-100 hover:bg-gray-200 rounded"
          >
            Academic-style AI text
          </button>
        </div>
      </div>
    </div>
  );
};

export default HumanizeAI;
