import React, { useState } from 'react';
import { api, EnhanceTextParams } from '../app/api';
import { toast } from 'react-hot-toast';

const EnhanceWriting: React.FC = () => {
  const [text, setText] = useState('');
  const [task, setTask] = useState<'enhance' | 'rewrite' | 'paraphrase'>('enhance');
  const [enhancedText, setEnhancedText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) {
      toast.error('Please enter some text');
      return;
    }

    setLoading(true);
    try {
      const params: EnhanceTextParams = { text, task };
      const result = await api.language.enhanceText(params);
      setEnhancedText(result);
    } catch (error) {
      console.error('Error enhancing text:', error);
      toast.error('Failed to enhance text');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = () => {
    if (enhancedText) {
      navigator.clipboard.writeText(enhancedText);
      toast.success('Enhanced text copied to clipboard');
    }
  };

  const getTaskDescription = () => {
    switch (task) {
      case 'enhance':
        return 'Improve your writing to make it more engaging and professional';
      case 'rewrite':
        return 'Rewrite your text to improve clarity and flow';
      case 'paraphrase':
        return 'Paraphrase your text while preserving its meaning';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold gradient-text">Enhance Writing</h1>
        <p className="mt-2 text-gray-600">
          {getTaskDescription()}
        </p>
      </div>

      <div className="card max-w-3xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="task" className="block text-sm font-medium text-gray-700 mb-1">
              Task
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setTask('enhance')}
                className={`py-2 px-4 rounded-md ${
                  task === 'enhance'
                    ? 'bg-primary-dark text-white'
                    : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                }`}
              >
                Enhance
              </button>
              <button
                type="button"
                onClick={() => setTask('rewrite')}
                className={`py-2 px-4 rounded-md ${
                  task === 'rewrite'
                    ? 'bg-primary-dark text-white'
                    : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                }`}
              >
                Rewrite
              </button>
              <button
                type="button"
                onClick={() => setTask('paraphrase')}
                className={`py-2 px-4 rounded-md ${
                  task === 'paraphrase'
                    ? 'bg-primary-dark text-white'
                    : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                }`}
              >
                Paraphrase
              </button>
            </div>
          </div>

          <div>
            <label htmlFor="text" className="block text-sm font-medium text-gray-700 mb-1">
              Your Text
            </label>
            <textarea
              id="text"
              rows={6}
              className="input-field"
              placeholder="Enter text to enhance..."
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
            {loading ? 'Processing...' : task === 'enhance' ? 'Enhance' : task === 'rewrite' ? 'Rewrite' : 'Paraphrase'}
          </button>
        </form>
      </div>

      {/* Results Section */}
      {enhancedText && (
        <div className="card max-w-3xl mx-auto">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800">
              {task === 'enhance' ? 'Enhanced Text' : task === 'rewrite' ? 'Rewritten Text' : 'Paraphrased Text'}
            </h2>
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
            <p className="whitespace-pre-wrap">{enhancedText}</p>
          </div>
        </div>
      )}

      <div className="max-w-3xl mx-auto">
        <h2 className="text-xl font-semibold text-gray-800 mb-2">Example Texts to Try</h2>
        <div className="grid grid-cols-1 gap-2">
          <button
            onClick={() => setText("Learning a new language is hard. It takes a lot of time and you need to practice every day. Many people give up because they don't see results fast.")}
            className="text-left p-2 bg-gray-100 hover:bg-gray-200 rounded"
          >
            Simple text about language learning
          </button>
          <button
            onClick={() => setText("I think that the book was good. The characters were interesting and the plot was exciting. I would recommend it to others who like this genre.")}
            className="text-left p-2 bg-gray-100 hover:bg-gray-200 rounded"
          >
            Basic book review
          </button>
        </div>
      </div>
    </div>
  );
};

export default EnhanceWriting;
