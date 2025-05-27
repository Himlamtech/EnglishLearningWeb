import React from 'react';

// Loading Spinner Component
export const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg'; color?: string }> = ({ 
  size = 'md', 
  color = 'text-primary' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className={`${sizeClasses[size]} ${color} animate-spin`}>
      <svg className="w-full h-full" fill="none" viewBox="0 0 24 24">
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  );
};

// Pulse Loading Component
export const PulseLoader: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`flex space-x-2 ${className}`}>
    <div className="w-3 h-3 bg-primary rounded-full animate-pulse-dot"></div>
    <div className="w-3 h-3 bg-primary rounded-full animate-pulse-dot" style={{ animationDelay: '0.2s' }}></div>
    <div className="w-3 h-3 bg-primary rounded-full animate-pulse-dot" style={{ animationDelay: '0.4s' }}></div>
  </div>
);

// Skeleton Components
export const SkeletonCard: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`card animate-pulse ${className}`}>
    <div className="skeleton h-6 w-3/4 mb-4"></div>
    <div className="skeleton h-4 w-full mb-2"></div>
    <div className="skeleton h-4 w-5/6 mb-2"></div>
    <div className="skeleton h-4 w-2/3"></div>
  </div>
);

export const SkeletonFlashcard: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`card h-64 animate-pulse ${className}`}>
    <div className="h-full flex flex-col justify-between">
      <div className="text-center">
        <div className="skeleton h-8 w-32 mx-auto mb-2"></div>
        <div className="skeleton h-4 w-24 mx-auto"></div>
      </div>
      <div className="skeleton h-4 w-48 mx-auto"></div>
      <div className="flex justify-between items-center">
        <div className="skeleton h-8 w-16"></div>
        <div className="skeleton h-8 w-20"></div>
      </div>
    </div>
  </div>
);

export const SkeletonStats: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`grid grid-cols-1 md:grid-cols-3 gap-6 ${className}`}>
    {[1, 2, 3].map((i) => (
      <div key={i} className="card animate-pulse">
        <div className="skeleton h-6 w-32 mb-2"></div>
        <div className="skeleton h-10 w-16"></div>
      </div>
    ))}
  </div>
);

// Page Loading Component
export const PageLoader: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="text-center">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-gray-600 animate-pulse">{message}</p>
    </div>
  </div>
);

// Button Loading State
export const LoadingButton: React.FC<{
  loading: boolean;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit';
}> = ({ loading, children, className = '', onClick, disabled, type = 'button' }) => (
  <button
    type={type}
    onClick={onClick}
    disabled={disabled || loading}
    className={`btn-primary relative ${className} ${loading ? 'cursor-not-allowed' : ''}`}
  >
    {loading && (
      <div className="absolute inset-0 flex items-center justify-center">
        <LoadingSpinner size="sm" color="text-white" />
      </div>
    )}
    <span className={loading ? 'opacity-0' : 'opacity-100'}>
      {children}
    </span>
  </button>
);

// Shimmer Effect Component
export const ShimmerCard: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`card shimmer ${className}`}>
    <div className="h-6 bg-gray-200 rounded mb-4"></div>
    <div className="h-4 bg-gray-200 rounded mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-5/6 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-2/3"></div>
  </div>
);

// Progress Bar Component
export const ProgressBar: React.FC<{
  progress: number;
  className?: string;
  showPercentage?: boolean;
  animated?: boolean;
}> = ({ progress, className = '', showPercentage = true, animated = true }) => (
  <div className={`w-full ${className}`}>
    <div className="progress-bar">
      <div 
        className={`progress-fill ${animated ? 'transition-all duration-500' : ''}`}
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      />
    </div>
    {showPercentage && (
      <div className="text-sm text-gray-600 mt-1 text-center">
        {Math.round(progress)}%
      </div>
    )}
  </div>
);

// Typing Animation Component
export const TypingIndicator: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`flex items-center space-x-1 ${className}`}>
    <span className="text-gray-500">Typing</span>
    <div className="flex space-x-1">
      <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
      <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
      <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
    </div>
  </div>
);
