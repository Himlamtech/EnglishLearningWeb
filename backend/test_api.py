#!/usr/bin/env python3
"""
Automated test script for FlashAI backend API endpoints
"""

import requests
import json
import time
import sys
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored terminal output
init()

# API Base URL
BASE_URL = "http://localhost:8000"

def print_header(text):
    """Print a section header"""
    print(f"\n{Fore.BLUE}{'=' * 50}")
    print(f"{Fore.BLUE}{text.center(50)}")
    print(f"{Fore.BLUE}{'=' * 50}{Style.RESET_ALL}")

def print_success(text):
    """Print a success message"""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text):
    """Print an error message"""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_info(text):
    """Print an info message"""
    print(f"{Fore.YELLOW}ℹ {text}{Style.RESET_ALL}")

def test_health_check():
    """Test the health check endpoint"""
    print_header("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200 and response.json().get("status") == "ok":
            print_success("Health check passed")
            return True
        else:
            print_error(f"Health check failed with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check failed with error: {str(e)}")
        return False

def test_flashcard_generation():
    """Test flashcard generation endpoint"""
    print_header("Testing Flashcard Generation")
    try:
        data = {"word": "hello", "targetLanguage": "auto"}
        response = requests.post(f"{BASE_URL}/flashcards", json=data)
        
        if response.status_code == 200:
            flashcard = response.json()
            print_success("Flashcard generated successfully")
            print_info(f"Word: {flashcard.get('word')}")
            print_info(f"Translation: {flashcard.get('translatedWord')}")
            print_info(f"Pronunciation: {flashcard.get('pronunciation')}")
            print_info(f"Synonyms: {', '.join(flashcard.get('synonyms', []))}")
            return flashcard
        else:
            print_error(f"Flashcard generation failed with status code {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Flashcard generation failed with error: {str(e)}")
        return None

def test_get_flashcards():
    """Test getting all flashcards endpoint"""
    print_header("Testing Get All Flashcards")
    try:
        response = requests.get(f"{BASE_URL}/flashcards")
        
        if response.status_code == 200:
            flashcards = response.json()
            print_success(f"Retrieved {len(flashcards)} flashcards successfully")
            return flashcards
        else:
            print_error(f"Get flashcards failed with status code {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Get flashcards failed with error: {str(e)}")
        return None

def test_mark_flashcard_learned(word):
    """Test marking a flashcard as learned"""
    print_header("Testing Mark Flashcard as Learned")
    try:
        response = requests.put(f"{BASE_URL}/flashcards/{word}/learned", params={"is_learned": True})
        
        if response.status_code == 200:
            print_success(f"Marked flashcard '{word}' as learned successfully")
            return True
        else:
            print_error(f"Mark as learned failed with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Mark as learned failed with error: {str(e)}")
        return False

def test_grammar_check():
    """Test grammar checking endpoint"""
    print_header("Testing Grammar Check")
    try:
        text = "She have a cat and dog."
        response = requests.post(f"{BASE_URL}/grammar-check", json={"text": text})
        
        if response.status_code == 200:
            result = response.json()
            print_success("Grammar check successful")
            print_info(f"Original text: {text}")
            print_info(f"Corrected text: {result.get('correctedText')}")
            print_info(f"Errors found: {', '.join(result.get('errors', []))}")
            return result
        else:
            print_error(f"Grammar check failed with status code {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Grammar check failed with error: {str(e)}")
        return None

def test_enhance_text():
    """Test text enhancement endpoint"""
    print_header("Testing Text Enhancement")
    try:
        text = "The cat was sitting on the mat. It was happy."
        tasks = ["rewrite", "paraphrase", "enhance"]
        
        for task in tasks:
            print_info(f"Testing {task} task...")
            response = requests.post(f"{BASE_URL}/enhance-text", 
                                   json={"text": text, "task": task})
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"{task.capitalize()} successful")
                print_info(f"Original text: {text}")
                print_info(f"Enhanced text: {result.get('enhancedText')}")
            else:
                print_error(f"{task.capitalize()} failed with status code {response.status_code}")
                
        return True
    except Exception as e:
        print_error(f"Text enhancement failed with error: {str(e)}")
        return False

def test_humanize_text():
    """Test humanizing AI text endpoint"""
    print_header("Testing Humanize AI Text")
    try:
        text = "The aforementioned analysis indicates that the utilization of artificial intelligence in educational contexts can potentially yield significant positive outcomes for student learning experiences."
        response = requests.post(f"{BASE_URL}/humanize-text", json={"text": text})
        
        if response.status_code == 200:
            result = response.json()
            print_success("Humanize text successful")
            print_info(f"Original text: {text}")
            print_info(f"Humanized text: {result.get('humanizedText')}")
            return result
        else:
            print_error(f"Humanize text failed with status code {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Humanize text failed with error: {str(e)}")
        return None

def test_ai_probability():
    """Test AI probability detection endpoint"""
    print_header("Testing AI Probability Check")
    try:
        # Test with likely AI-generated text
        ai_text = "The utilization of deep learning methodologies in conjunction with natural language processing techniques has revolutionized the field of artificial intelligence in recent years, resulting in unprecedented advancements in machine translation capabilities."
        
        # Test with likely human text
        human_text = "I went to the store yesterday. It was really crowded. I bought some milk and eggs."
        
        for idx, text in enumerate([ai_text, human_text]):
            label = "AI-like" if idx == 0 else "Human-like"
            print_info(f"Testing {label} text...")
            
            response = requests.post(f"{BASE_URL}/ai-probability", json={"text": text})
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"AI probability check successful for {label} text")
                print_info(f"Probability: {result.get('probability')}%")
            else:
                print_error(f"AI probability check failed with status code {response.status_code}")
                
        return True
    except Exception as e:
        print_error(f"AI probability check failed with error: {str(e)}")
        return False

def test_chat():
    """Test chatbot endpoint"""
    print_header("Testing Chatbot")
    try:
        messages = [
            {"role": "user", "content": "What's the difference between 'their', 'there', and 'they're'?"}
        ]
        
        response = requests.post(f"{BASE_URL}/chat", json={"messages": messages})
        
        if response.status_code == 200:
            result = response.json()
            print_success("Chat successful")
            print_info(f"User message: {messages[0]['content']}")
            print_info(f"AI response: {result.get('response')[:100]}...")
            return result
        else:
            print_error(f"Chat failed with status code {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Chat failed with error: {str(e)}")
        return None

def main():
    """Run all tests"""
    print_header("FlashAI Backend API Tests")
    
    # Check if backend is running
    if not test_health_check():
        print_error("Backend server is not running or not responding. Please start the server first.")
        sys.exit(1)
        
    tests_passed = 0
    tests_failed = 0
    
    # Test flashcard generation
    flashcard = test_flashcard_generation()
    if flashcard:
        tests_passed += 1
    else:
        tests_failed += 1
        
    # Test get flashcards
    flashcards = test_get_flashcards()
    if flashcards is not None:
        tests_passed += 1
    else:
        tests_failed += 1
        
    # Test mark as learned if we have flashcards
    if flashcards and len(flashcards) > 0:
        word = flashcards[0].get('word')
        if test_mark_flashcard_learned(word):
            tests_passed += 1
        else:
            tests_failed += 1
    else:
        print_info("Skipping mark as learned test - no flashcards available")
        
    # Test grammar check
    if test_grammar_check():
        tests_passed += 1
    else:
        tests_failed += 1
        
    # Test enhance text
    if test_enhance_text():
        tests_passed += 1
    else:
        tests_failed += 1
        
    # Test humanize text
    if test_humanize_text():
        tests_passed += 1
    else:
        tests_failed += 1
        
    # Test AI probability
    if test_ai_probability():
        tests_passed += 1
    else:
        tests_failed += 1
        
    # Test chat
    if test_chat():
        tests_passed += 1
    else:
        tests_failed += 1
        
    # Print summary
    print_header("Test Summary")
    print_info(f"Tests passed: {tests_passed}")
    print_info(f"Tests failed: {tests_failed}")
    
    if tests_failed == 0:
        print_success("All tests passed!")
    else:
        print_error(f"{tests_failed} tests failed.")
    
if __name__ == "__main__":
    main() 