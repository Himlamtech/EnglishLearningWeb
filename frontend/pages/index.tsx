import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { getFlashcards, Flashcard } from '../app/api/flashcardApi';
import FlashcardCard from '../app/components/FlashcardCard';
import { LoadingSpinner, SkeletonStats, SkeletonFlashcard, ProgressBar } from '../app/components/LoadingComponents';
import { toast } from 'react-hot-toast';
import {
  BookOpenIcon,
  AcademicCapIcon,
  ChartBarIcon,
  SparklesIcon,
  FireIcon,
  TrophyIcon
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFlashcards();
  }, []);

  const fetchFlashcards = async () => {
    setLoading(true);
    try {
      const data = await getFlashcards();
      setFlashcards(data);
    } catch (error) {
      console.error('Failed to fetch flashcards:', error);
      toast.error('Failed to load flashcards');
    } finally {
      setLoading(false);
    }
  };

  // Calculate statistics
  const totalFlashcards = flashcards.length;
  const learnedFlashcards = flashcards.filter(card => card.isLearned).length;
  const learningProgress = totalFlashcards > 0 ? (learnedFlashcards / totalFlashcards) * 100 : 0;

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-start/20 via-purple-500/20 to-blue-end/20 rounded-3xl blur-3xl"></div>
        <div className="relative">
          <h1 className="text-5xl md:text-6xl font-bold gradient-text-animated animate-bounce-in">
            FlashAI Dashboard
          </h1>
          <p className="mt-4 text-xl text-gray-600 dark:text-gray-300 animate-slide-in-up">
            Your AI-powered language learning assistant
          </p>
          <div className="mt-6 flex justify-center">
            <SparklesIcon className="h-8 w-8 text-yellow-500 animate-float" />
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {loading ? (
        <SkeletonStats />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card floating-card bg-gradient-to-br from-blue-start to-blue-end text-white animate-slide-in-up">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold flex items-center">
                  <BookOpenIcon className="h-6 w-6 mr-2" />
                  Total Flashcards
                </h2>
                <p className="text-4xl font-bold mt-2 animate-bounce-in">{totalFlashcards}</p>
              </div>
              <div className="text-white/30">
                <ChartBarIcon className="h-12 w-12" />
              </div>
            </div>
          </div>

          <div className="card floating-card bg-gradient-to-br from-green-400 to-green-600 text-white animate-slide-in-up" style={{ animationDelay: '0.1s' }}>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold flex items-center">
                  <AcademicCapIcon className="h-6 w-6 mr-2" />
                  Learned
                </h2>
                <p className="text-4xl font-bold mt-2 animate-bounce-in">{learnedFlashcards}</p>
              </div>
              <div className="text-white/30">
                <TrophyIcon className="h-12 w-12" />
              </div>
            </div>
          </div>

          <div className="card floating-card bg-gradient-to-br from-purple-500 to-pink-500 text-white animate-slide-in-up" style={{ animationDelay: '0.2s' }}>
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h2 className="text-xl font-semibold flex items-center">
                  <FireIcon className="h-6 w-6 mr-2" />
                  Progress
                </h2>
                <p className="text-4xl font-bold mt-2 animate-bounce-in">{learningProgress.toFixed(1)}%</p>
                <ProgressBar
                  progress={learningProgress}
                  className="mt-3"
                  showPercentage={false}
                />
              </div>
              <div className="text-white/30">
                <ChartBarIcon className="h-12 w-12" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Features Section */}
      <div>
        <h2 className="text-3xl font-bold mb-8 text-gray-800 dark:text-gray-200 text-center animate-slide-in-up">
          🚀 Powerful Features
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <Link href="/flashcard-generation" className="card floating-card group animate-slide-in-up hover:bg-gradient-to-br hover:from-blue-50 hover:to-blue-100 dark:hover:from-blue-900/20 dark:hover:to-blue-800/20">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-start to-blue-end rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <SparklesIcon className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-primary-dark dark:text-primary-light group-hover:text-primary-darker">Flashcard Generation</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">Create AI-powered flashcards for language learning</p>
            </div>
          </Link>

          <Link href="/learn-flashcard" className="card floating-card group animate-slide-in-up hover:bg-gradient-to-br hover:from-green-50 hover:to-green-100 dark:hover:from-green-900/20 dark:hover:to-green-800/20" style={{ animationDelay: '0.1s' }}>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-green-400 to-green-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <AcademicCapIcon className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-primary-dark dark:text-primary-light group-hover:text-green-600">Learn Flashcards</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">Study and review your flashcards</p>
            </div>
          </Link>

          <Link href="/chatbot" className="card floating-card group animate-slide-in-up hover:bg-gradient-to-br hover:from-purple-50 hover:to-purple-100 dark:hover:from-purple-900/20 dark:hover:to-purple-800/20" style={{ animationDelay: '0.2s' }}>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-primary-dark dark:text-primary-light group-hover:text-purple-600">Language Chatbot</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">Chat with an AI to improve your language skills</p>
            </div>
          </Link>

          <Link href="/grammar-checking" className="card floating-card group animate-slide-in-up hover:bg-gradient-to-br hover:from-orange-50 hover:to-orange-100 dark:hover:from-orange-900/20 dark:hover:to-orange-800/20" style={{ animationDelay: '0.3s' }}>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-orange-400 to-red-500 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-primary-dark dark:text-primary-light group-hover:text-orange-600">Grammar Checking</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">Check and correct grammar in your writing</p>
            </div>
          </Link>
        </div>
      </div>

      {/* Recent Flashcards */}
      <div>
        <h2 className="text-3xl font-bold mb-8 text-gray-800 dark:text-gray-200 text-center animate-slide-in-up">
          📚 Recent Flashcards
        </h2>
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <SkeletonFlashcard key={i} />
            ))}
          </div>
        ) : flashcards.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {flashcards.slice(0, 6).map((flashcard, index) => (
              <div
                key={flashcard.word}
                className="animate-slide-in-up"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <FlashcardCard
                  flashcard={flashcard}
                  onUpdate={fetchFlashcards}
                />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 animate-fade-in-scale">
            <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 rounded-full flex items-center justify-center">
              <BookOpenIcon className="h-12 w-12 text-gray-400 dark:text-gray-500" />
            </div>
            <h3 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-2">No flashcards yet</h3>
            <p className="text-gray-500 dark:text-gray-500 mb-6">Start your learning journey by creating your first flashcard!</p>
            <Link href="/flashcard-generation" className="btn-primary inline-flex items-center">
              <SparklesIcon className="h-5 w-5 mr-2" />
              Create Your First Flashcard
            </Link>
          </div>
        )}

        {flashcards.length > 6 && (
          <div className="text-center mt-8 animate-slide-in-up">
            <Link href="/learn-flashcard" className="btn-secondary inline-flex items-center">
              <BookOpenIcon className="h-5 w-5 mr-2" />
              View All {totalFlashcards} Flashcards
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;