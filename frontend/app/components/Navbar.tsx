import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Disclosure } from '@headlessui/react';
import { Bars3Icon, XMarkIcon, SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { useTheme } from './ThemeProvider';

// Array of navigation items
const navigation = [
  { name: 'Dashboard', href: '/' },
  { name: 'Flashcard Generation', href: '/flashcard-generation' },
  { name: 'Learn Flashcard', href: '/learn-flashcard' },
  { name: 'Chatbot', href: '/chatbot' },
  { name: 'Grammar Checking', href: '/grammar-checking' },
  { name: 'AI Checking', href: '/ai-checking' },
  { name: 'Humanize AI', href: '/humanize-ai' },
  { name: 'Enhance Writing', href: '/enhance-writing' },
];

const Navbar: React.FC = () => {
  const pathname = usePathname();
  const { theme, toggleTheme } = useTheme();

  return (
    <Disclosure as="nav" className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md shadow-lg border-b border-white/20 dark:border-gray-700/20 sticky top-0 z-50">
      {({ open }) => (
        <>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <Link href="/" className="flex items-center group">
                    <span className="text-2xl font-bold gradient-text-animated group-hover:scale-105 transition-transform duration-300">
                      FlashAI
                    </span>
                  </Link>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-1">
                  {navigation.map((item) => (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={`inline-flex items-center px-3 py-1 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105 ${
                        pathname === item.href
                          ? 'bg-primary/10 text-primary-dark border-b-2 border-primary-dark shadow-md'
                          : 'text-gray-600 dark:text-gray-300 hover:bg-primary/5 hover:text-primary-dark dark:hover:text-primary-light'
                      }`}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
              </div>

              <div className="flex items-center space-x-4">
                {/* Theme Toggle Button */}
                <button
                  onClick={toggleTheme}
                  className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all duration-300 transform hover:scale-110"
                  aria-label="Toggle theme"
                >
                  {theme === 'light' ? (
                    <MoonIcon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
                  ) : (
                    <SunIcon className="h-5 w-5 text-yellow-500" />
                  )}
                </button>

                {/* Mobile menu button */}
                <div className="sm:hidden">
                  <Disclosure.Button className="inline-flex items-center justify-center p-2 rounded-lg text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary transition-all duration-300">
                    <span className="sr-only">Open main menu</span>
                    {open ? (
                      <XMarkIcon className="block h-6 w-6 transform rotate-180 transition-transform duration-300" aria-hidden="true" />
                    ) : (
                      <Bars3Icon className="block h-6 w-6 transition-transform duration-300" aria-hidden="true" />
                    )}
                  </Disclosure.Button>
                </div>
              </div>
            </div>
          </div>

          <Disclosure.Panel className="sm:hidden bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-t border-gray-200 dark:border-gray-700">
            <div className="pt-2 pb-3 space-y-1 px-4">
              {navigation.map((item, index) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`block px-4 py-3 rounded-lg text-base font-medium transition-all duration-300 transform hover:scale-105 animate-slide-in-up ${
                    pathname === item.href
                      ? 'bg-primary/10 border-l-4 border-primary-dark text-primary-dark shadow-md'
                      : 'text-gray-600 dark:text-gray-300 hover:bg-primary/5 hover:text-primary-dark dark:hover:text-primary-light'
                  }`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  {item.name}
                </Link>
              ))}
            </div>
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
};

export default Navbar;