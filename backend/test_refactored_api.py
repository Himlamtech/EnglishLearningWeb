#!/usr/bin/env python3
"""
Test script for the refactored FlashAI backend API.

This script tests the new architecture and verifies that all components
work together correctly.
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_configuration():
    """Test the configuration system."""
    print("Testing Configuration System...")
    
    try:
        from config import Config
        
        # Test configuration validation
        print(f"✓ Configuration loaded successfully")
        print(f"  - API Key configured: {bool(Config.OPENAI_API_KEY)}")
        print(f"  - API Base URL: {Config.API_BASE_URL}")
        print(f"  - Model: {Config.OPENAI_MODEL}")
        print(f"  - Default timeout: {Config.DEFAULT_TIMEOUT}s")
        print(f"  - Max retries: {Config.MAX_RETRIES}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {str(e)}")
        return False


async def test_exceptions():
    """Test the custom exception system."""
    print("\nTesting Exception System...")
    
    try:
        from utils.exceptions import (
            FlashAIException, APIException, ValidationException, 
            StorageException, ConfigurationException
        )
        
        # Test exception creation and serialization
        exc = ValidationException(
            "Test validation error",
            field="test_field",
            value="test_value"
        )
        
        exc_dict = exc.to_dict()
        assert "error" in exc_dict
        assert "message" in exc_dict
        assert exc_dict["message"] == "Test validation error"
        
        print("✓ Exception system working correctly")
        return True
    except Exception as e:
        print(f"✗ Exception test failed: {str(e)}")
        return False


async def test_validators():
    """Test the validation system."""
    print("\nTesting Validation System...")
    
    try:
        from utils.validators import (
            validate_text_input, validate_word_input, 
            validate_language_code, validate_enhancement_task
        )
        
        # Test text validation
        validated_text = validate_text_input("Hello world", min_length=1, max_length=100)
        assert validated_text == "Hello world"
        
        # Test word validation
        validated_word = validate_word_input("hello")
        assert validated_word == "hello"
        
        # Test language code validation
        validated_lang = validate_language_code("en")
        assert validated_lang == "en"
        
        # Test enhancement task validation
        validated_task = validate_enhancement_task("rewrite")
        assert validated_task == "rewrite"
        
        print("✓ Validation system working correctly")
        return True
    except Exception as e:
        print(f"✗ Validation test failed: {str(e)}")
        return False


async def test_prompt_templates():
    """Test the prompt template system."""
    print("\nTesting Prompt Template System...")
    
    try:
        from utils.prompt_templates import PromptTemplateEngine
        
        engine = PromptTemplateEngine()
        
        # Test flashcard prompt generation
        flashcard_prompt = engine.generate_flashcard_prompt("hello", "auto")
        assert "messages" in flashcard_prompt
        assert "functions" in flashcard_prompt
        assert len(flashcard_prompt["messages"]) >= 2
        
        # Test grammar check prompt generation
        grammar_prompt = engine.generate_grammar_check_prompt("She have a cat.")
        assert "messages" in grammar_prompt
        assert "functions" in grammar_prompt
        
        print("✓ Prompt template system working correctly")
        return True
    except Exception as e:
        print(f"✗ Prompt template test failed: {str(e)}")
        return False


async def test_repository():
    """Test the repository layer."""
    print("\nTesting Repository Layer...")
    
    try:
        from repositories.flashcard_repository import FlashcardRepository
        import tempfile
        import os
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Initialize repository with test file
            repo = FlashcardRepository(temp_path)
            
            # Test adding a flashcard
            test_flashcard = {
                "word": "test",
                "translatedWord": "thử nghiệm",
                "pronunciation": "/test/",
                "synonyms": ["trial", "exam", "check"],
                "isLearned": False
            }
            
            success = repo.add(test_flashcard)
            assert success, "Failed to add flashcard"
            
            # Test retrieving flashcards
            flashcards = repo.get_all()
            assert len(flashcards) == 1
            assert flashcards[0]["word"] == "test"
            
            # Test finding flashcard
            found = repo.find_by_word("test")
            assert found is not None
            assert found["word"] == "test"
            
            # Test updating flashcard
            success = repo.update("test", {"isLearned": True})
            assert success
            
            # Test statistics
            stats = repo.get_statistics()
            assert stats["total_flashcards"] == 1
            assert stats["learned_flashcards"] == 1
            
            print("✓ Repository layer working correctly")
            return True
            
        finally:
            # Clean up test file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        print(f"✗ Repository test failed: {str(e)}")
        return False


async def test_services():
    """Test the service layer (without actual API calls)."""
    print("\nTesting Service Layer...")
    
    try:
        from services.flashcard_service import FlashcardService
        from services.ai_service import AIService
        import tempfile
        import os
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Test FlashcardService initialization
            from repositories.flashcard_repository import FlashcardRepository
            repo = FlashcardRepository(temp_path)
            service = FlashcardService(repo)
            
            # Test getting all flashcards (should be empty initially)
            flashcards = service.get_all_flashcards()
            assert isinstance(flashcards, list)
            
            # Test statistics
            stats = service.get_learning_statistics()
            assert isinstance(stats, dict)
            assert "total_flashcards" in stats
            
            # Test AIService initialization
            ai_service = AIService()
            assert ai_service is not None
            
            print("✓ Service layer working correctly")
            return True
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        print(f"✗ Service test failed: {str(e)}")
        return False


async def test_models():
    """Test the Pydantic models."""
    print("\nTesting Pydantic Models...")
    
    try:
        from models import Flashcard, FlashcardCreate, FlashcardUpdate, TextInput
        
        # Test Flashcard model
        flashcard = Flashcard(
            word="test",
            translatedWord="thử nghiệm",
            pronunciation="/test/",
            synonyms=["trial", "exam"],
            isLearned=False
        )
        assert flashcard.word == "test"
        assert flashcard.isLearned == False
        
        # Test FlashcardCreate model
        create_data = FlashcardCreate(word="hello", targetLanguage="vi")
        assert create_data.word == "hello"
        assert create_data.targetLanguage == "vi"
        
        # Test TextInput model
        text_input = TextInput(text="Hello world")
        assert text_input.text == "Hello world"
        
        print("✓ Pydantic models working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Model test failed: {str(e)}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("FlashAI Backend Refactoring Test Suite")
    print("=" * 60)
    
    tests = [
        test_configuration,
        test_exceptions,
        test_validators,
        test_prompt_templates,
        test_repository,
        test_services,
        test_models
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The refactored backend is working correctly.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
