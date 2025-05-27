import React from 'react';
import { AppProps } from 'next/app';
import { Toaster } from 'react-hot-toast';
import Navbar from '../app/components/Navbar';
import { ThemeProvider } from '../app/components/ThemeProvider';
import '../app/styles/globals.css';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '12px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#ffffff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#ffffff',
            },
          },
        }}
      />
      <div className="min-h-screen bg-gradient-to-br from-background-light to-background-dark dark:from-gray-900 dark:to-gray-800 transition-all duration-300">
        <Navbar />
        <main className="container mx-auto px-4 py-8 max-w-7xl">
          <div className="animate-fade-in-scale">
            <Component {...pageProps} />
          </div>
        </main>
      </div>
    </ThemeProvider>
  );
}

export default MyApp;