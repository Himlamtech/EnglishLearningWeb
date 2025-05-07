import React from 'react';
import { AppProps } from 'next/app';
import { Toaster } from 'react-hot-toast';
import Navbar from '../components/Navbar';
import '../styles/globals.css';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Toaster position="top-right" />
      <Navbar />
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <Component {...pageProps} />
      </main>
    </>
  );
}

export default MyApp; 