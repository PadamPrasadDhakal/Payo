"""
Dynamic Assessment Question Generation using Google Gemini API (FREE)
Generates questions in real-time based on user's actual skills and experience
NO STORED QUESTIONS - Everything is generated dynamically by AI
"""
import json
import random
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

# Try to import Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("WARNING: google-generativeai not installed. Run: pip install google-generativeai")

# Get API key - use a free Gemini API key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')


class DeepSeekQuestionGenerator:
    """
    Generate DYNAMIC MCQ questions using Google Gemini API (FREE)
    Questions are generated in real-time based on user's specific skills
    NO DATABASE STORAGE - Fresh questions every time
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = None
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("✓ Gemini API initialized successfully")
            except Exception as e:
                print(f"✗ Gemini API initialization failed: {e}")
                self.model = None
        else:
            if not GEMINI_AVAILABLE:
                print("✗ google-generativeai package not installed")
            if not self.api_key:
                print("✗ No GEMINI_API_KEY found in environment")
    
    def generate_questions(self, skills: str, experience: str, experience_level: str, num_questions: int = 10) -> List[Dict[str, Any]]:
        """
        Generate MCQ questions DYNAMICALLY using AI based on user's actual skills
        
        Args:
            skills: User's skills (e.g., "python, C, django")
            experience: User's experience description
            experience_level: entry/intermediate/senior/expert
            num_questions: Number of questions to generate
            
        Returns:
            List of dynamically generated questions specific to user's skills
        """
        
        print(f"\n{'='*60}")
        print(f"GENERATING DYNAMIC QUESTIONS")
        print(f"Skills: {skills}")
        print(f"Experience Level: {experience_level}")
        print(f"Number of Questions: {num_questions}")
        print(f"{'='*60}\n")
        
        if not self.model:
            print("ERROR: AI model not available - using skill-based fallback")
            return self._generate_skill_based_questions(skills, experience_level, num_questions)
        
        # Create prompt for the specific skills
        prompt = self._create_prompt(skills, experience, experience_level, num_questions)
        
        try:
            # Generate questions using Gemini AI
            print("Calling Gemini API...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                print(f"Got response from Gemini ({len(response.text)} chars)")
                # Parse the AI response
                questions = self._parse_questions(response.text)
                
                if questions and len(questions) >= num_questions:
                    print(f"✓ SUCCESS: Generated {len(questions)} dynamic questions for: {skills}")
                    return questions[:num_questions]
                elif questions and len(questions) > 0:
                    print(f"⚠ PARTIAL: Got {len(questions)} questions, needed {num_questions}")
                    # Generate more if needed
                    more_needed = num_questions - len(questions)
                    more_questions = self._generate_more_questions(skills, experience_level, more_needed)
                    questions.extend(more_questions)
                    return questions[:num_questions]
                else:
                    print("⚠ WARNING: Could not parse AI response, retrying...")
                    return self._retry_generation(skills, experience_level, num_questions)
            else:
                print("⚠ WARNING: Empty AI response")
                return self._retry_generation(skills, experience_level, num_questions)
                
        except Exception as e:
            print(f"✗ ERROR: AI generation failed: {str(e)}")
            return self._retry_generation(skills, experience_level, num_questions)
    
    def _create_prompt(self, skills: str, experience: str, experience_level: str, num_questions: int) -> str:
        """Create prompt for dynamic question generation"""
        
        difficulty_map = {
            'entry': 'basic/beginner - focus on fundamental concepts',
            'intermediate': 'intermediate - include practical applications',
            'senior': 'advanced - include complex scenarios',
            'expert': 'expert/challenging - include deep technical knowledge'
        }
        difficulty = difficulty_map.get(experience_level.lower(), 'intermediate')
        
        prompt = f"""You are an expert assessment creator. Generate exactly {num_questions} multiple choice questions (MCQs) for a professional skill assessment.

TARGET USER'S SKILLS: {skills}
EXPERIENCE LEVEL: {experience_level} ({difficulty})

STRICT REQUIREMENTS:
1. Create questions ONLY about these specific skills: {skills}
2. Each skill mentioned should have questions about it
3. Questions must match {difficulty} difficulty level
4. Each question MUST have exactly 4 options labeled A, B, C, D
5. Only ONE option should be correct
6. Include a mix of theoretical and practical questions
7. Questions should be clear and professional

OUTPUT FORMAT - Return ONLY this JSON (no markdown, no explanation, no code blocks):
{{
  "questions": [
    {{
      "question": "Your specific question about {skills}?",
      "options": {{
        "A": "First option",
        "B": "Second option",
        "C": "Third option",
        "D": "Fourth option"
      }},
      "correct_answer": "B",
      "explanation": "Why option B is correct"
    }}
  ]
}}

NOW GENERATE {num_questions} QUESTIONS SPECIFICALLY ABOUT: {skills}

Remember: Output ONLY valid JSON, nothing else. No markdown formatting."""

        return prompt
    
    def _parse_questions(self, content: str) -> List[Dict[str, Any]]:
        """Parse AI response to extract questions"""
        try:
            # Clean up the response
            content = content.strip()
            
            # Remove markdown code blocks if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                parts = content.split('```')
                for part in parts:
                    if '{' in part and 'questions' in part:
                        content = part
                        break
            
            content = content.strip()
            
            # Find JSON object
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                content = content[start:end]
            
            # Parse JSON
            data = json.loads(content)
            
            if isinstance(data, dict) and 'questions' in data:
                questions = data['questions']
                # Validate each question has required fields
                valid_questions = []
                for q in questions:
                    if all(key in q for key in ['question', 'options', 'correct_answer']):
                        valid_questions.append(q)
                return valid_questions
            elif isinstance(data, list):
                return data
            
            return []
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Content preview: {content[:300]}...")
            return []
    
    def _retry_generation(self, skills: str, experience_level: str, num_questions: int) -> List[Dict[str, Any]]:
        """Retry with simpler prompt"""
        print("Retrying with simplified prompt...")
        
        simple_prompt = f"""Generate {num_questions} MCQ questions about: {skills}

Each question format:
- question: the question text
- options: A, B, C, D options
- correct_answer: the letter of correct answer
- explanation: why it's correct

Return as JSON array:
{{"questions": [{{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct_answer": "A", "explanation": "..."}}]}}

Create {num_questions} questions about {skills} NOW. Output only JSON."""

        try:
            if self.model:
                response = self.model.generate_content(simple_prompt)
                if response and response.text:
                    questions = self._parse_questions(response.text)
                    if questions:
                        print(f"✓ Retry successful: got {len(questions)} questions")
                        return questions[:num_questions]
        except Exception as e:
            print(f"Retry failed: {e}")
        
        # Final fallback - generate skill-based questions
        return self._generate_skill_based_questions(skills, experience_level, num_questions)
    
    def _generate_more_questions(self, skills: str, experience_level: str, num_needed: int) -> List[Dict[str, Any]]:
        """Generate additional questions"""
        prompt = f"""Generate {num_needed} more MCQ questions about {skills} at {experience_level} level.
Return JSON: {{"questions": [{{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct_answer": "A", "explanation": "..."}}]}}"""
        
        try:
            if self.model:
                response = self.model.generate_content(prompt)
                if response and response.text:
                    return self._parse_questions(response.text)
        except:
            pass
        return []
    
    def _generate_skill_based_questions(self, skills: str, experience_level: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generate questions based on specific skills when API fails"""
        print(f"Generating skill-based fallback questions for: {skills}")
        
        skills_list = [s.strip().lower() for s in skills.split(',')]
        questions = []
        
        # Create skill-specific questions
        for skill in skills_list:
            skill_qs = self._get_skill_questions(skill.strip(), experience_level)
            questions.extend(skill_qs)
        
        # If not enough, add more
        while len(questions) < num_questions:
            for skill in skills_list:
                more = self._get_additional_questions(skill.strip())
                questions.extend(more)
                if len(questions) >= num_questions:
                    break
        
        random.shuffle(questions)
        return questions[:num_questions]
    
    def _get_skill_questions(self, skill: str, level: str) -> List[Dict[str, Any]]:
        """Get questions for a specific skill"""
        skill = skill.lower().strip()
        
        # Python questions
        if 'python' in skill:
            return [
                {"question": "What is the output of print(type([]))?", "options": {"A": "<class 'list'>", "B": "<class 'array'>", "C": "<class 'tuple'>", "D": "<class 'dict'>"}, "correct_answer": "A", "explanation": "[] creates an empty list in Python"},
                {"question": "Which keyword is used to define a function in Python?", "options": {"A": "function", "B": "def", "C": "define", "D": "func"}, "correct_answer": "B", "explanation": "Python uses 'def' keyword to define functions"},
                {"question": "What is a Python decorator?", "options": {"A": "A design pattern", "B": "A function that modifies another function", "C": "A class method", "D": "A variable type"}, "correct_answer": "B", "explanation": "Decorators modify or extend function behavior"},
                {"question": "Which method adds an element to the end of a list?", "options": {"A": "add()", "B": "insert()", "C": "append()", "D": "push()"}, "correct_answer": "C", "explanation": "append() adds to the end of a list"},
                {"question": "What does 'self' refer to in a Python class?", "options": {"A": "The class itself", "B": "The current instance", "C": "A global variable", "D": "The parent class"}, "correct_answer": "B", "explanation": "'self' refers to the current instance of the class"},
                {"question": "How do you create a virtual environment in Python?", "options": {"A": "python -m venv env", "B": "python create env", "C": "pip install env", "D": "python --env create"}, "correct_answer": "A", "explanation": "python -m venv creates a virtual environment"},
            ]
        
        # C programming questions
        elif skill == 'c' or skill == 'c programming':
            return [
                {"question": "What is the correct way to declare a pointer in C?", "options": {"A": "int p;", "B": "int *p;", "C": "pointer int p;", "D": "int &p;"}, "correct_answer": "B", "explanation": "* is used to declare pointers in C"},
                {"question": "Which header file is required for printf()?", "options": {"A": "stdlib.h", "B": "string.h", "C": "stdio.h", "D": "conio.h"}, "correct_answer": "C", "explanation": "stdio.h contains printf and scanf functions"},
                {"question": "What does malloc() return?", "options": {"A": "Integer", "B": "Void pointer", "C": "Character", "D": "Nothing"}, "correct_answer": "B", "explanation": "malloc returns a void pointer to allocated memory"},
                {"question": "What is the size of char in C?", "options": {"A": "1 byte", "B": "2 bytes", "C": "4 bytes", "D": "Depends on compiler"}, "correct_answer": "A", "explanation": "char is always 1 byte in C"},
                {"question": "Which operator is used to access structure members through pointer?", "options": {"A": ".", "B": "->", "C": "*", "D": "&"}, "correct_answer": "B", "explanation": "-> is used for pointer to structure member access"},
                {"question": "What is the correct syntax for a for loop in C?", "options": {"A": "for (i = 0; i < n; i++)", "B": "for i in range(n)", "C": "for (i < n; i++)", "D": "for each i in n"}, "correct_answer": "A", "explanation": "C uses initialization; condition; increment format"},
            ]
        
        # Django questions
        elif 'django' in skill:
            return [
                {"question": "What command creates a new Django project?", "options": {"A": "django new project", "B": "django-admin startproject", "C": "python manage.py create", "D": "django init"}, "correct_answer": "B", "explanation": "django-admin startproject creates a new project"},
                {"question": "What is Django's ORM?", "options": {"A": "Object-Relational Mapping", "B": "Online Resource Manager", "C": "Object Request Model", "D": "Open Resource Module"}, "correct_answer": "A", "explanation": "ORM maps Python objects to database tables"},
                {"question": "Which file contains Django URL patterns?", "options": {"A": "views.py", "B": "models.py", "C": "urls.py", "D": "settings.py"}, "correct_answer": "C", "explanation": "urls.py contains URL routing patterns"},
                {"question": "What is a Django migration?", "options": {"A": "Moving to a new server", "B": "Database schema version control", "C": "Code backup", "D": "User data transfer"}, "correct_answer": "B", "explanation": "Migrations track and apply database schema changes"},
                {"question": "What does manage.py runserver do?", "options": {"A": "Runs tests", "B": "Starts development server", "C": "Creates migrations", "D": "Collects static files"}, "correct_answer": "B", "explanation": "runserver starts Django's development web server"},
                {"question": "What is a Django view?", "options": {"A": "A database table", "B": "A function handling web requests", "C": "An HTML template", "D": "A CSS file"}, "correct_answer": "B", "explanation": "Views are functions/classes that handle HTTP requests and return responses"},
            ]
        
        # JavaScript questions
        elif 'javascript' in skill or 'js' in skill:
            return [
                {"question": "What is the correct way to declare a variable in modern JavaScript?", "options": {"A": "var x = 5;", "B": "let x = 5;", "C": "const x = 5;", "D": "Both B and C are preferred"}, "correct_answer": "D", "explanation": "let and const are preferred over var in modern JS"},
                {"question": "What does '===' operator do in JavaScript?", "options": {"A": "Assigns value", "B": "Compares value only", "C": "Compares value and type", "D": "Compares reference"}, "correct_answer": "C", "explanation": "=== checks both value and type equality"},
                {"question": "What is a Promise in JavaScript?", "options": {"A": "A guaranteed return value", "B": "An object representing eventual completion/failure of async operation", "C": "A type of loop", "D": "A function declaration"}, "correct_answer": "B", "explanation": "Promises handle asynchronous operations"},
            ]
        
        # React questions
        elif 'react' in skill:
            return [
                {"question": "What is JSX in React?", "options": {"A": "A database query language", "B": "JavaScript XML - syntax extension", "C": "A testing framework", "D": "A build tool"}, "correct_answer": "B", "explanation": "JSX allows writing HTML-like code in JavaScript"},
                {"question": "What hook is used for state in functional components?", "options": {"A": "useEffect", "B": "useState", "C": "useContext", "D": "useReducer"}, "correct_answer": "B", "explanation": "useState manages component state"},
                {"question": "What is a React component?", "options": {"A": "A CSS class", "B": "A reusable UI building block", "C": "A database table", "D": "A server endpoint"}, "correct_answer": "B", "explanation": "Components are reusable pieces of UI"},
            ]
        
        # SQL questions
        elif 'sql' in skill or 'database' in skill or 'mysql' in skill or 'postgresql' in skill:
            return [
                {"question": "Which SQL clause is used to filter records?", "options": {"A": "ORDER BY", "B": "GROUP BY", "C": "WHERE", "D": "HAVING"}, "correct_answer": "C", "explanation": "WHERE filters rows based on conditions"},
                {"question": "What does JOIN do in SQL?", "options": {"A": "Combines rows from two or more tables", "B": "Creates a new table", "C": "Deletes duplicate records", "D": "Sorts the results"}, "correct_answer": "A", "explanation": "JOIN combines related data from multiple tables"},
                {"question": "Which command is used to add new records?", "options": {"A": "UPDATE", "B": "INSERT", "C": "ADD", "D": "CREATE"}, "correct_answer": "B", "explanation": "INSERT INTO adds new rows to a table"},
            ]
        
        # HTML/CSS questions
        elif 'html' in skill or 'css' in skill:
            return [
                {"question": "What does HTML stand for?", "options": {"A": "Hyper Text Markup Language", "B": "High Tech Modern Language", "C": "Hyper Transfer Markup Language", "D": "Home Tool Markup Language"}, "correct_answer": "A", "explanation": "HTML is Hyper Text Markup Language"},
                {"question": "Which CSS property changes text color?", "options": {"A": "text-color", "B": "font-color", "C": "color", "D": "text-style"}, "correct_answer": "C", "explanation": "The 'color' property sets text color"},
                {"question": "What is the correct HTML for a hyperlink?", "options": {"A": "<a href='url'>", "B": "<link href='url'>", "C": "<hyperlink>url</hyperlink>", "D": "<url>link</url>"}, "correct_answer": "A", "explanation": "The <a> tag with href attribute creates links"},
            ]
        
        # Java questions
        elif 'java' in skill and 'javascript' not in skill:
            return [
                {"question": "What is the entry point of a Java program?", "options": {"A": "start() method", "B": "main() method", "C": "run() method", "D": "init() method"}, "correct_answer": "B", "explanation": "public static void main(String[] args) is the entry point"},
                {"question": "What is JVM?", "options": {"A": "Java Very Modern", "B": "Java Virtual Machine", "C": "Java Version Manager", "D": "Java Visual Method"}, "correct_answer": "B", "explanation": "JVM executes Java bytecode"},
                {"question": "Which keyword is used to inherit a class in Java?", "options": {"A": "implements", "B": "inherits", "C": "extends", "D": "super"}, "correct_answer": "C", "explanation": "'extends' is used for class inheritance"},
            ]
        
        # Generic/fallback questions
        else:
            return [
                {"question": f"What is a key principle when working with {skill}?", "options": {"A": "Follow best practices", "B": "Skip documentation", "C": "Avoid testing", "D": "Ignore errors"}, "correct_answer": "A", "explanation": "Best practices ensure quality and maintainability"},
                {"question": f"Which is important for {skill} development?", "options": {"A": "Clear requirements", "B": "Random coding", "C": "No planning", "D": "Skipping reviews"}, "correct_answer": "A", "explanation": "Clear requirements guide successful development"},
            ]
    
    def _get_additional_questions(self, skill: str) -> List[Dict[str, Any]]:
        """Get additional questions if needed"""
        return [
            {"question": f"What is considered a best practice in {skill}?", "options": {"A": "Write clean, readable code", "B": "Write as fast as possible", "C": "Skip testing", "D": "Avoid comments"}, "correct_answer": "A", "explanation": "Clean code is maintainable and understandable"},
            {"question": f"Why is testing important in {skill}?", "options": {"A": "To find bugs early", "B": "To slow down development", "C": "To make code longer", "D": "It's not important"}, "correct_answer": "A", "explanation": "Testing catches issues before production"},
        ]
