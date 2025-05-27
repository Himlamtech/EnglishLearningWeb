"""
Advanced prompt templates using expert-level prompt engineering techniques.

This module implements Chain of Thought (CoT), Tree of Thought (ToT),
and React (Reasoning + Acting) methodologies for optimal AI responses.
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class PromptType(Enum):
    """Enumeration of available prompt types."""
    FLASHCARD_GENERATION = "flashcard_generation"
    GRAMMAR_CHECK = "grammar_check"
    TEXT_ENHANCEMENT = "text_enhancement"
    TEXT_HUMANIZATION = "text_humanization"
    AI_DETECTION = "ai_detection"
    LANGUAGE_CHAT = "language_chat"


class PromptTemplateEngine:
    """
    Advanced prompt template engine implementing expert prompt engineering techniques.

    Features:
    - Chain of Thought (CoT) reasoning
    - Tree of Thought (ToT) structured thinking
    - React (Reasoning + Acting) methodology
    - Context-aware prompt generation
    - Role-based prompt customization
    """

    @staticmethod
    def generate_flashcard_prompt(word: str, target_language: str = "auto") -> Dict[str, Any]:
        """
        Generate an expert-level flashcard creation prompt using CoT methodology.

        Args:
            word: The word to create a flashcard for
            target_language: Target language for translation

        Returns:
            Dictionary containing system and user messages with function definition
        """

        # Determine translation direction with reasoning
        if target_language.lower() in ["vietnamese", "vi"]:
            direction_context = "English to Vietnamese"
            language_note = "The input word is in English and should be translated to Vietnamese."
        elif target_language.lower() in ["english", "en"]:
            direction_context = "Vietnamese to English"
            language_note = "The input word is in Vietnamese and should be translated to English."
        else:
            direction_context = "Auto-detect"
            language_note = "Auto-detect the language and translate accordingly (English ↔ Vietnamese)."

        system_message = f"""You are an expert language learning specialist and lexicographer with deep knowledge of English and Vietnamese languages. Your task is to create comprehensive, accurate flashcards for language learners.

ROLE & EXPERTISE:
- Expert in English-Vietnamese translation and linguistics
- Specialized in creating educational content for language learners
- Deep understanding of pronunciation, etymology, and usage patterns

REASONING PROCESS (Chain of Thought):
1. ANALYZE the input word:
   - Identify the source language
   - Determine the word's part of speech and context
   - Consider multiple meanings if applicable

2. TRANSLATE with precision:
   - Provide the most accurate and commonly used translation
   - Consider cultural context and usage frequency
   - Ensure translation is appropriate for language learners

3. GENERATE pronunciation:
   - Use International Phonetic Alphabet (IPA) notation
   - Ensure accuracy for the source language
   - Make it helpful for pronunciation learning

4. SELECT synonyms:
   - Choose 3 high-quality synonyms in the SOURCE language
   - Prioritize commonly used alternatives
   - Ensure synonyms are appropriate for the context

QUALITY STANDARDS:
- Accuracy: All translations must be linguistically correct
- Relevance: Content must be useful for language learners
- Clarity: Information should be easy to understand
- Consistency: Follow standard linguistic conventions

CURRENT TASK: {direction_context} translation
CONTEXT: {language_note}"""

        user_message = f"""Please create a comprehensive flashcard for the word: "{word}"

Follow this step-by-step reasoning process:

STEP 1 - WORD ANALYSIS:
Think about the word "{word}":
- What language is this word in?
- What is its primary meaning and usage?
- Are there any special considerations for translation?

STEP 2 - TRANSLATION STRATEGY:
- Determine the most accurate translation
- Consider the target audience (language learners)
- Ensure the translation is commonly used and practical

STEP 3 - PRONUNCIATION GUIDE:
- Generate accurate IPA pronunciation for the source word
- Ensure it helps learners pronounce the word correctly

STEP 4 - SYNONYM SELECTION:
- Choose 3 relevant synonyms in the SAME language as the source word
- Prioritize commonly used alternatives
- Ensure they match the context and meaning

Please provide your response using the create_flashcard function with accurate, educational content."""

        function_definition = {
            "name": "create_flashcard",
            "description": "Create a comprehensive language learning flashcard with translation, pronunciation, and synonyms",
            "parameters": {
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": "The original word (exactly as provided)"
                    },
                    "translatedWord": {
                        "type": "string",
                        "description": "Accurate translation of the word to the target language"
                    },
                    "pronunciation": {
                        "type": "string",
                        "description": "IPA pronunciation notation for the original word"
                    },
                    "synonyms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of exactly 3 synonyms in the SAME language as the original word",
                        "minItems": 3,
                        "maxItems": 3
                    }
                },
                "required": ["word", "translatedWord", "pronunciation", "synonyms"]
            }
        }

        return {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "functions": [function_definition],
            "function_call": {"name": "create_flashcard"}
        }

    @staticmethod
    def generate_grammar_check_prompt(text: str) -> Dict[str, Any]:
        """
        Generate an expert-level grammar checking prompt using ToT methodology.

        Args:
            text: Text to check for grammar errors

        Returns:
            Dictionary containing system and user messages with function definition
        """

        system_message = """You are an expert English grammar specialist and writing coach with advanced knowledge of linguistic analysis and error detection.

EXPERTISE AREAS:
- Advanced English grammar and syntax
- Error pattern recognition and classification
- Writing improvement and style enhancement
- Educational feedback for language learners

ANALYSIS METHODOLOGY (Tree of Thought):

BRANCH 1 - STRUCTURAL ANALYSIS:
├── Sentence structure and syntax
├── Subject-verb agreement patterns
├── Tense consistency and usage
└── Clause relationships and dependencies

BRANCH 2 - GRAMMATICAL ELEMENTS:
├── Parts of speech accuracy
├── Article usage (a, an, the)
├── Preposition selection and placement
└── Pronoun reference and agreement

BRANCH 3 - STYLE AND CLARITY:
├── Word choice and vocabulary
├── Sentence flow and readability
├── Redundancy and conciseness
└── Formal vs. informal register

BRANCH 4 - COMMON ERROR PATTERNS:
├── Homophones (their/there/they're)
├── Irregular verb forms
├── Plural and possessive forms
└── Comma splices and run-on sentences

QUALITY STANDARDS:
- Comprehensive: Identify ALL grammar errors
- Educational: Provide clear explanations
- Accurate: Ensure corrections are linguistically sound
- Helpful: Focus on learning and improvement"""

        user_message = f"""Please perform a comprehensive grammar analysis of the following text using the Tree of Thought methodology:

TEXT TO ANALYZE: "{text}"

ANALYSIS PROCESS:

STEP 1 - INITIAL SCAN:
Read through the text and identify potential issues across all grammatical categories.

STEP 2 - SYSTEMATIC EXAMINATION:
Examine each sentence for:
- Subject-verb agreement
- Tense consistency
- Pronoun usage
- Article placement
- Preposition accuracy
- Punctuation correctness

STEP 3 - ERROR CLASSIFICATION:
Categorize each error found and determine the appropriate correction.

STEP 4 - COMPREHENSIVE CORRECTION:
Provide the fully corrected version while maintaining the original meaning and style.

STEP 5 - EDUCATIONAL FEEDBACK:
List specific errors with clear explanations to help the user learn.

Please use the grammar_check function to provide your detailed analysis."""

        function_definition = {
            "name": "grammar_check",
            "description": "Perform comprehensive grammar analysis and provide corrections with detailed explanations",
            "parameters": {
                "type": "object",
                "properties": {
                    "correctedText": {
                        "type": "string",
                        "description": "The text with all grammar errors corrected, maintaining original meaning and style"
                    },
                    "errors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Detailed list of grammar errors found with clear explanations and learning points"
                    }
                },
                "required": ["correctedText", "errors"]
            }
        }

        return {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "functions": [function_definition],
            "function_call": {"name": "grammar_check"}
        }

    @staticmethod
    def generate_text_enhancement_prompt(text: str, task: str) -> Dict[str, Any]:
        """
        Generate an expert-level text enhancement prompt using React methodology.

        Args:
            text: Text to enhance
            task: Type of enhancement (rewrite, paraphrase, enhance)

        Returns:
            Dictionary containing system and user messages
        """

        task_definitions = {
            "rewrite": {
                "goal": "Rewrite the text to improve clarity, flow, and readability while preserving the original meaning",
                "focus": "sentence structure, word choice, and overall coherence",
                "outcome": "A clearer, more polished version of the original text"
            },
            "paraphrase": {
                "goal": "Express the same ideas using different words and sentence structures",
                "focus": "vocabulary variation, syntactic diversity, and semantic preservation",
                "outcome": "A fresh expression of the same concepts with different wording"
            },
            "enhance": {
                "goal": "Elevate the text to be more engaging, professional, and impactful",
                "focus": "sophistication, persuasiveness, and stylistic improvement",
                "outcome": "A more compelling and professionally written version"
            }
        }

        task_info = task_definitions.get(task, task_definitions["enhance"])

        system_message = f"""You are an expert writing coach. Your task is to {task} text to make it better.

Focus on: {task_info['focus']}
Goal: {task_info['goal']}

Provide ONLY the improved text without explanations, analysis, or methodology descriptions."""

        user_message = f"""Task: {task.upper()} the following text.

Original: "{text}"

Goal: {task_info['goal']}

Provide ONLY the improved version without explanations, analysis, or step-by-step breakdowns.

Requirements:
- Maintain the original meaning
- {task_info['focus']}
- Make it sound natural and engaging
- Keep it concise and clear

Enhanced version:"""

        return {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        }

    @staticmethod
    def generate_humanization_prompt(text: str) -> Dict[str, Any]:
        """
        Generate a prompt to make AI-generated text sound more human and natural.

        Args:
            text: AI-generated text to humanize

        Returns:
            Dictionary containing system and user messages
        """

        system_message = """You are an expert at making text sound natural and human. Transform formal or robotic text into conversational, authentic language.

Provide ONLY the humanized text without explanations or analysis."""

        user_message = f"""Make this text sound more natural and human:

Original: "{text}"

Provide ONLY the humanized version without explanations or analysis.

Requirements:
- Sound conversational and natural
- Remove formal/robotic language
- Add personality and warmth
- Keep the same meaning
- Make it feel authentic

Humanized version:"""

        return {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        }

    @staticmethod
    def generate_ai_detection_prompt(text: str) -> Dict[str, Any]:
        """
        Generate a prompt to analyze the probability that text was AI-generated.

        Args:
            text: Text to analyze for AI generation probability

        Returns:
            Dictionary containing system and user messages
        """

        system_message = """You are an expert in AI-generated text detection with deep knowledge of language patterns, writing styles, and the characteristics that distinguish human from AI writing.

EXPERTISE:
- AI text generation patterns and signatures
- Human writing characteristics and variations
- Statistical analysis of language patterns
- Contextual and stylistic analysis

DETECTION METHODOLOGY (Tree of Thought):

BRANCH 1 - LINGUISTIC PATTERNS:
├── Vocabulary sophistication and variation
├── Sentence structure complexity and diversity
├── Grammatical perfection vs. natural imperfections
└── Word choice patterns and frequency

BRANCH 2 - STYLISTIC MARKERS:
├── Tone consistency and naturalness
├── Personal voice and authenticity markers
├── Cultural and contextual appropriateness
└── Emotional expression and personality

BRANCH 3 - STRUCTURAL ANALYSIS:
├── Paragraph organization and flow
├── Logical progression and coherence
├── Transition quality and naturalness
└── Overall composition structure

BRANCH 4 - AI SIGNATURES:
├── Overly formal or academic language
├── Repetitive phrasing patterns
├── Perfect grammar without natural variations
└── Generic or template-like expressions

ANALYSIS CRITERIA:
- Language naturalness and authenticity
- Presence of AI-typical patterns
- Human writing characteristics
- Statistical likelihood assessment

PROBABILITY SCALE:
0-20%: Very likely human-written
21-40%: Probably human-written
41-60%: Uncertain/Mixed indicators
61-80%: Probably AI-generated
81-100%: Very likely AI-generated"""

        user_message = f"""Please analyze the following text to determine the probability that it was generated by AI:

TEXT TO ANALYZE: "{text}"

ANALYSIS PROCESS:

STEP 1 - LINGUISTIC PATTERN ANALYSIS:
- Examine vocabulary sophistication and variation
- Assess sentence structure diversity
- Check for grammatical perfection vs. natural imperfections
- Analyze word choice patterns

STEP 2 - STYLISTIC EVALUATION:
- Evaluate tone consistency and naturalness
- Look for personal voice and authenticity markers
- Assess cultural and contextual appropriateness
- Check emotional expression quality

STEP 3 - STRUCTURAL ASSESSMENT:
- Review paragraph organization and flow
- Examine logical progression
- Assess transition quality
- Evaluate overall composition

STEP 4 - AI SIGNATURE DETECTION:
- Look for overly formal language
- Check for repetitive patterns
- Assess grammatical perfection level
- Identify generic expressions

STEP 5 - PROBABILITY CALCULATION:
Based on your analysis, provide a probability percentage (0-100) that this text was AI-generated.

Please respond with just the probability number (0-100) representing the likelihood this text was AI-generated."""

        return {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        }

    @staticmethod
    def generate_language_chat_prompt(messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generate a prompt for language learning chat assistance.

        Args:
            messages: Conversation history

        Returns:
            Dictionary containing system and user messages
        """

        system_message = """You are a friendly English tutor. Help students learn English through conversation and practical examples.

Be:
- Encouraging and supportive
- Clear and concise
- Practical with real examples
- Conversational, not academic

Focus on helping students practice and improve their English skills."""

        # Format conversation history
        conversation_context = ""
        if len(messages) > 1:
            conversation_context = "\n\nCONVERSATION HISTORY:\n"
            for msg in messages[:-1]:
                role_label = "Student" if msg["role"] == "user" else "Tutor"
                conversation_context += f"{role_label}: {msg['content']}\n"

        current_question = messages[-1]["content"] if messages else ""

        user_message = f"""Help the student with their English learning question:{conversation_context}

Student's question: "{current_question}"

Provide a helpful, encouraging response with practical examples."""

        return {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        }
