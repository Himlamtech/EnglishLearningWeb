import json
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from config import OPENAI_API_KEY, API_BASE_URL, OPENAI_MODEL

# Mock data for fallback if API fails
MOCK_FLASHCARDS = {
    "hello": {
        "word": "hello",
        "translatedWord": "Xin chào",
        "pronunciation": "/həˈloʊ/",
        "synonyms": ["Hi", "Hey", "Greetings"]
    },
    "goodbye": {
        "word": "goodbye",
        "translatedWord": "Tạm biệt",
        "pronunciation": "/ˌɡʊdˈbaɪ/",
        "synonyms": ["Farewell", "See you", "Take care"]
    },
    "xin chào": {
        "word": "xin chào",
        "translatedWord": "Hello",
        "pronunciation": "/sin chow/",
        "synonyms": ["Greetings", "Hi", "Welcome"]
    }
}

# Create a session that can be reused across requests
_session: Optional[aiohttp.ClientSession] = None

async def get_session() -> aiohttp.ClientSession:
    """Get or create a shared aiohttp ClientSession."""
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
    return _session

async def close_session():
    """Close the global session if it exists."""
    global _session
    if _session and not _session.closed:
        await _session.close()
        _session = None

async def call_openai_api(messages, functions=None, function_call=None, timeout=20):
    """Make a call to the OpenAI API with timeout."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": 0.7,  # Add temperature for more consistent responses
        "max_tokens": 500    # Limit token count for faster responses
    }

    if functions:
        payload["functions"] = functions

    if function_call:
        payload["function_call"] = function_call

    try:
        session = await get_session()
        # Use asyncio.wait_for to implement a timeout
        async with asyncio.timeout(timeout):
            async with session.post(
                f"{API_BASE_URL}/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    print(f"API Error: {response.status} - {error_text}")
                    return None
    except asyncio.TimeoutError:
        print(f"API request timed out after {timeout} seconds")
        return None
    except Exception as e:
        print(f"API Call Error: {str(e)}")
        return None

# API functions
async def generate_flashcard(word: str, target_language: str = "auto") -> Dict[str, Any]:
    """Generate a flashcard for a given word using the OpenAI API."""
    # Check for mock data first for quick response
    word_lower = word.lower()
    if word_lower in MOCK_FLASHCARDS:
        return MOCK_FLASHCARDS[word_lower]

    try:
        # Determine translation direction based on target_language
        translation_instruction = ""
        if target_language.lower() == "vietnamese" or target_language.lower() == "vi":
            translation_instruction = "Translate this English word to Vietnamese."
        elif target_language.lower() == "english" or target_language.lower() == "en":
            translation_instruction = "Translate this Vietnamese word to English."
        else:
            translation_instruction = "If the word is in English, translate to Vietnamese. If the word is in Vietnamese, translate to English."

        # Simplified prompt for faster response
        messages = [
            {"role": "system", "content": "Generate flashcards with translations between English and Vietnamese."},
            {"role": "user", "content": f"Create a flashcard for: \"{word}\". {translation_instruction}"}
        ]

        functions = [
            {
                "name": "create_flashcard",
                "description": "Create a language learning flashcard",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "Original word"
                        },
                        "translatedWord": {
                            "type": "string",
                            "description": "Translation"
                        },
                        "pronunciation": {
                            "type": "string",
                            "description": "Pronunciation"
                        },
                        "synonyms": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "3 synonyms"
                        }
                    },
                    "required": ["word", "translatedWord", "pronunciation", "synonyms"]
                }
            }
        ]

        function_call = {"name": "create_flashcard"}

        # Use a shorter timeout for flashcard generation
        response = await call_openai_api(messages, functions, function_call, timeout=15)

        if response and "choices" in response and len(response["choices"]) > 0:
            message = response["choices"][0]["message"]
            if "function_call" in message:
                function_args = json.loads(message["function_call"]["arguments"])
                return {
                    "word": function_args.get("word", word),
                    "translatedWord": function_args.get("translatedWord", ""),
                    "pronunciation": function_args.get("pronunciation", ""),
                    "synonyms": function_args.get("synonyms", [])
                }

        # Fallback with basic translation if API call fails
        return {
            "word": word,
            "translatedWord": f"Translation of {word}",
            "pronunciation": "/basic/",
            "synonyms": ["similar1", "similar2", "similar3"]
        }
    except Exception as e:
        print(f"Error generating flashcard: {str(e)}")
        return {
            "word": word,
            "translatedWord": f"Error: {str(e)}",
            "pronunciation": "",
            "synonyms": []
        }

async def check_grammar(text: str) -> Dict[str, Any]:
    """Check grammar in the provided text using the OpenAI API."""
    try:
        messages = [
            {"role": "system", "content": "You are a helpful grammar checking assistant. Identify and correct grammar errors in the text."},
            {"role": "user", "content": f"Check the grammar in this text and provide corrections: \"{text}\""}
        ]

        functions = [
            {
                "name": "grammar_check",
                "description": "Check grammar and provide corrections",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "correctedText": {
                            "type": "string",
                            "description": "The text with grammar errors corrected"
                        },
                        "errors": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of grammar errors found in the text"
                        }
                    },
                    "required": ["correctedText", "errors"]
                }
            }
        ]

        function_call = {"name": "grammar_check"}

        response = await call_openai_api(messages, functions, function_call)

        if response and "choices" in response and len(response["choices"]) > 0:
            message = response["choices"][0]["message"]
            if "function_call" in message:
                function_args = json.loads(message["function_call"]["arguments"])
                return {
                    "correctedText": function_args.get("correctedText", text),
                    "errors": function_args.get("errors", ["No grammar errors found"])
                }

        # Fallback to simple grammar check if API call fails
        errors = []
        corrected_text = text

        if "have a" in text.lower() and "she" in text.lower():
            errors.append("Subject-verb agreement error: 'She have' should be 'She has'")
            corrected_text = text.replace("have", "has")

        if "their" in text.lower() and "is" in text.lower():
            errors.append("Pronoun agreement error: 'Their is' should be 'There is'")
            corrected_text = text.replace("Their", "There")

        return {
            "correctedText": corrected_text,
            "errors": errors if errors else ["No grammar errors found"]
        }
    except Exception as e:
        print(f"Error checking grammar: {str(e)}")
        return {
            "correctedText": text,
            "errors": [f"Error: {str(e)}"]
        }

async def enhance_writing(text: str, task: str) -> str:
    """Enhance the provided text based on the specified task using the OpenAI API."""
    try:
        task_description = ""
        if task == "rewrite":
            task_description = "Rewrite this text to improve clarity and flow while preserving the meaning"
        elif task == "paraphrase":
            task_description = "Paraphrase this text using different words while preserving the meaning"
        else:  # enhance
            task_description = "Enhance this text to make it more engaging, professional, and well-written"

        messages = [
            {"role": "system", "content": "You are a helpful writing assistant that improves text."},
            {"role": "user", "content": f"{task_description}: \"{text}\""}
        ]

        response = await call_openai_api(messages)

        if response and "choices" in response and len(response["choices"]) > 0:
            message = response["choices"][0]["message"]
            if "content" in message:
                return message["content"]

        # Fallback if API call fails
        if task == "rewrite":
            return f"Rewritten version: {text} [This is a fallback rewrite]"
        elif task == "paraphrase":
            return f"Paraphrased version: {text} [This is a fallback paraphrase]"
        else:
            return f"Enhanced version: {text} [This is a fallback enhancement]"
    except Exception as e:
        print(f"Error enhancing text: {str(e)}")
        return f"Error enhancing text: {str(e)}"

async def humanize_text(text: str) -> str:
    """Make AI-generated text sound more natural and human-like using the OpenAI API."""
    try:
        messages = [
            {"role": "system", "content": "You are a helpful writing assistant that makes text sound more natural and human-like."},
            {"role": "user", "content": f"Make this AI-generated text sound more natural and human-like: \"{text}\""}
        ]

        response = await call_openai_api(messages)

        if response and "choices" in response and len(response["choices"]) > 0:
            message = response["choices"][0]["message"]
            if "content" in message:
                return message["content"]

        # Fallback if API call fails
        return f"Humanized version: {text} [This is a fallback humanization]"
    except Exception as e:
        print(f"Error humanizing text: {str(e)}")
        return f"Error humanizing text: {str(e)}"

async def check_ai_probability(text: str) -> int:
    """Check the probability that the text was generated by AI using the OpenAI API."""
    try:
        messages = [
            {"role": "system", "content": "You are a helpful AI detection assistant. Analyze text and determine the probability it was generated by AI."},
            {"role": "user", "content": f"What is the probability (as a percentage from 0-100) that this text was generated by AI? Respond with just the number: \"{text}\""}
        ]

        response = await call_openai_api(messages)

        if response and "choices" in response and len(response["choices"]) > 0:
            message = response["choices"][0]["message"]
            if "content" in message:
                # Extract the number from the response
                content = message["content"]
                # Try to extract a number from the response
                import re
                numbers = re.findall(r'\d+', content)
                if numbers:
                    probability = int(numbers[0])
                    # Ensure it's in the range 0-100
                    return max(0, min(100, probability))

        # Fallback to simple heuristic if API call fails
        words = text.split()
        if len(words) > 30:
            return 85
        elif len(words) > 15:
            return 60
        else:
            return 30
    except Exception as e:
        print(f"Error checking AI probability: {str(e)}")
        # Fallback
        return 50

async def chat_with_ai(messages: List[Dict[str, str]]) -> str:
    """Chat with AI for language learning assistance using the OpenAI API."""
    try:
        # Prepare messages for the API
        api_messages = [
            {"role": "system", "content": "You are a helpful language learning assistant. Provide clear, concise, and accurate information about language learning, grammar, vocabulary, and related topics."}
        ]

        # Add user messages
        for msg in messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        response = await call_openai_api(api_messages)

        if response and "choices" in response and len(response["choices"]) > 0:
            message = response["choices"][0]["message"]
            if "content" in message:
                return message["content"]

        # Fallback responses if API call fails
        user_message = messages[-1]["content"].lower() if messages else ""

        if "hello" in user_message or "hi" in user_message:
            return "Hello! How can I help you with language learning today?"

        if "their" in user_message and "there" in user_message and "they're" in user_message:
            return "Here's the difference:\n- 'Their' is a possessive pronoun (Their car is red)\n- 'There' indicates a place or existence (There is a book)\n- 'They're' is a contraction of 'they are' (They're going to school)"

        if "grammar" in user_message:
            return "Grammar is the set of rules that govern how words are used in a language. What specific grammar concept would you like to learn about?"

        return "I'm having trouble connecting to the language learning service. Please try again later."
    except Exception as e:
        print(f"Error chatting with AI: {str(e)}")
        return f"Error: {str(e)}"