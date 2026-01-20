"""
DeepSeek API Integration for Dynamic Assessment Question Generation
"""
# from pyglet import env
import requests
import json
import random
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('apikey_deepseek')

class DeepSeekQuestionGenerator:
    """Generate dynamic MCQ questions based on user skills and experience"""
    
    def __init__(self, api_key: str = api_key):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        # Minimal fallback question bank (only used if API fails)
        self.question_bank = self._build_minimal_fallback_bank()
        
    def generate_questions(self, skills: str, experience: str, experience_level: str, num_questions: int = 10) -> List[Dict[str, Any]]:
        """
        Generate MCQ questions dynamically using DeepSeek API based on user profile
        
        Args:
            skills: Comma-separated skills
            experience: User's experience text
            experience_level: entry/intermediate/senior/expert
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries with question, options, and correct answer
        """
        
        print(f"INFO: Using DeepSeek API to generate {num_questions} questions for skills: {skills}, level: {experience_level}")
        
        # Prepare the prompt
        prompt = self._create_prompt(skills, experience, experience_level, num_questions)
        
        try:
            # Make API request
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert professional interviewer who creates precise, relevant MCQ questions for skill assessment across ALL industries (technology, healthcare, finance, education, hospitality, construction, marketing, etc.). Always respond with valid JSON only."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 3000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse the JSON response
                questions = self._parse_questions(content)
                if questions and len(questions) >= num_questions:
                    print(f"SUCCESS: Generated {len(questions)} questions from DeepSeek API")
                    return questions[:num_questions]  # Ensure we return exactly num_questions
                elif questions and len(questions) > 0:
                    print(f"WARNING: API returned only {len(questions)} questions, requested {num_questions}")
                    # Fill remaining with fallback
                    remaining = num_questions - len(questions)
                    fallback = self._get_fallback_questions(skills, remaining)
                    return questions + fallback
                else:
                    print("WARNING: DeepSeek API returned no valid questions, using fallback")
                    return self._get_fallback_questions(skills, num_questions)
            else:
                print(f"ERROR: DeepSeek API Error: {response.status_code} - {response.text}")
                return self._get_fallback_questions(skills, num_questions)
                
        except Exception as e:
            print(f"ERROR: Exception while calling DeepSeek API: {str(e)}")
            return self._get_fallback_questions(skills, num_questions)
    
    def _create_prompt(self, skills: str, experience: str, experience_level: str, num_questions: int) -> str:
        """Create a detailed prompt for question generation across ALL industries"""
        
        difficulty_mapping = {
            'entry': 'beginner to intermediate',
            'intermediate': 'intermediate',
            'senior': 'intermediate to advanced',
            'expert': 'advanced'
        }
        difficulty = difficulty_mapping.get(experience_level, 'intermediate')
        
        prompt = f"""Generate {num_questions} multiple-choice questions for a professional skills assessment.

User Profile:
- Skills: {skills or 'General professional skills'}
- Experience Level: {experience_level or 'intermediate'}
- Experience: {experience[:200] if experience else 'Professional work experience'}

IMPORTANT INSTRUCTIONS:
1. Create questions SPECIFICALLY for the user's skills and industry (not just technology)
2. If skills include healthcare, create healthcare questions
3. If skills include finance/accounting, create finance/accounting questions
4. If skills include marketing, create marketing questions
5. If skills include hospitality, create hospitality questions
6. If skills include construction/engineering, create construction questions
7. If skills include education/teaching, create education questions
8. If skills include customer service, create customer service questions
9. Questions should be at {difficulty} difficulty level
10. Include practical, real-world scenario-based questions
11. Each question MUST have exactly 4 options (A, B, C, D)
12. Only ONE option should be correct
13. Questions should be clear, unambiguous, and professional

Response Format (MUST be valid JSON - NO markdown, NO code blocks, just pure JSON):
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      }},
      "correct_answer": "A",
      "explanation": "Brief explanation why this is correct"
    }}
  ]
}}

Generate exactly {num_questions} questions relevant to the user's skills: {skills}
Respond ONLY with the JSON object, no additional text or formatting."""
        
        return prompt
    
    def _parse_questions(self, content: str) -> List[Dict[str, Any]]:
        """Parse the API response and extract questions"""
        try:
            # Try to find JSON in the content
            content = content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            data = json.loads(content)
            
            if isinstance(data, dict) and 'questions' in data:
                return data['questions']
            elif isinstance(data, list):
                return data
            else:
                print("Unexpected response format")
                return []
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Content: {content}")
            return []
    
    def _get_fallback_questions(self, skills: str, num_questions: int = 10) -> List[Dict[str, Any]]:
        """Return fallback questions if API fails"""
        
        fallback = [
            {
                "question": "What does API stand for in software development?",
                "options": {
                    "A": "Application Programming Interface",
                    "B": "Advanced Programming Integration",
                    "C": "Automated Process Interface",
                    "D": "Application Process Integration"
                },
                "correct_answer": "A",
                "explanation": "API stands for Application Programming Interface"
            },
            {
                "question": "Which of the following is NOT a valid HTTP method?",
                "options": {
                    "A": "GET",
                    "B": "POST",
                    "C": "FETCH",
                    "D": "DELETE"
                },
                "correct_answer": "C",
                "explanation": "FETCH is not a standard HTTP method"
            },
            {
                "question": "What is the time complexity of binary search?",
                "options": {
                    "A": "O(n)",
                    "B": "O(log n)",
                    "C": "O(n²)",
                    "D": "O(1)"
                },
                "correct_answer": "B",
                "explanation": "Binary search has O(log n) time complexity"
            },
            {
                "question": "In Object-Oriented Programming, what does 'inheritance' mean?",
                "options": {
                    "A": "Creating multiple instances of a class",
                    "B": "A class acquiring properties from another class",
                    "C": "Hiding internal implementation details",
                    "D": "Grouping related functions together"
                },
                "correct_answer": "B",
                "explanation": "Inheritance allows a class to acquire properties and methods from parent class"
            },
            {
                "question": "Which database type is MongoDB?",
                "options": {
                    "A": "Relational Database",
                    "B": "NoSQL Document Database",
                    "C": "Graph Database",
                    "D": "Time-Series Database"
                },
                "correct_answer": "B",
                "explanation": "MongoDB is a NoSQL document-oriented database"
            },
            {
                "question": "What is the purpose of 'git commit' command?",
                "options": {
                    "A": "Upload changes to remote repository",
                    "B": "Save changes to local repository",
                    "C": "Create a new branch",
                    "D": "Merge two branches"
                },
                "correct_answer": "B",
                "explanation": "git commit saves changes to the local repository"
            },
            {
                "question": "In Python, which keyword is used to define a function?",
                "options": {
                    "A": "function",
                    "B": "define",
                    "C": "def",
                    "D": "func"
                },
                "correct_answer": "C",
                "explanation": "Python uses 'def' keyword to define functions"
            },
            {
                "question": "What does CSS stand for?",
                "options": {
                    "A": "Creative Style Sheets",
                    "B": "Cascading Style Sheets",
                    "C": "Computer Style Sheets",
                    "D": "Colorful Style Sheets"
                },
                "correct_answer": "B",
                "explanation": "CSS stands for Cascading Style Sheets"
            },
            {
                "question": "Which of the following is a JavaScript framework?",
                "options": {
                    "A": "Django",
                    "B": "Flask",
                    "C": "React",
                    "D": "Laravel"
                },
                "correct_answer": "C",
                "explanation": "React is a JavaScript library/framework for building user interfaces"
            },
            {
                "question": "What is the default port for HTTP?",
                "options": {
                    "A": "21",
                    "B": "80",
                    "C": "443",
                    "D": "8080"
                },
                "correct_answer": "B",
                "explanation": "HTTP uses port 80 by default"
            }
        ]
        
        return fallback[:num_questions]
    
    def _build_minimal_fallback_bank(self) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Build MINIMAL fallback question bank (only used if API fails)
        This is an emergency backup - primary questions come from DeepSeek API
        """
        return {
            # General questions that work across industries
            "general": {
                "entry": [
                    {
                        "question": "What does communication mean in a professional context?",
                        "options": {"A": "Exchanging information effectively", "B": "Talking loudly", "C": "Using email only", "D": "Avoiding conversations"},
                        "correct_answer": "A",
                        "explanation": "Professional communication involves clear information exchange"
                    },
                    {
                        "question": "What is teamwork?",
                        "options": {"A": "Collaborating with others toward common goals", "B": "Working alone", "C": "Competing with colleagues", "D": "Avoiding group projects"},
                        "correct_answer": "A",
                        "explanation": "Teamwork is cooperative effort toward shared objectives"
                    },
                    {
                        "question": "What is time management?",
                        "options": {"A": "Organizing and planning time effectively", "B": "Working overtime", "C": "Rushing through tasks", "D": "Ignoring deadlines"},
                        "correct_answer": "A",
                        "explanation": "Time management optimizes productivity through planning"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is problem-solving?",
                        "options": {"A": "Identifying and resolving issues systematically", "B": "Ignoring problems", "C": "Blaming others", "D": "Creating more problems"},
                        "correct_answer": "A",
                        "explanation": "Problem-solving involves systematic issue resolution"
                    },
                    {
                        "question": "What is professional ethics?",
                        "options": {"A": "Moral principles guiding workplace behavior", "B": "Company rules only", "C": "Personal preferences", "D": "Legal requirements only"},
                        "correct_answer": "A",
                        "explanation": "Professional ethics guide moral workplace conduct"
                    }
                ],
                "senior": [
                    {
                        "question": "What is strategic thinking?",
                        "options": {"A": "Long-term planning considering multiple factors", "B": "Quick decisions", "C": "Following orders", "D": "Avoiding planning"},
                        "correct_answer": "A",
                        "explanation": "Strategic thinking involves comprehensive long-term planning"
                    }
                ],
                "expert": [
                    {
                        "question": "What is change management?",
                        "options": {"A": "Guiding organizational transition effectively", "B": "Resisting change", "C": "Making random changes", "D": "Avoiding new methods"},
                        "correct_answer": "A",
                        "explanation": "Change management facilitates smooth organizational transitions"
                    }
                ]
            }
        }
    
    def _get_fallback_questions(self, skills: str, num_questions: int = 10) -> List[Dict[str, Any]]:
        """
        Return minimal fallback questions when API fails
        NOTE: This is only used as emergency backup when DeepSeek API is unavailable
        """
        print(f"WARNING: Using fallback questions (API unavailable)")
        
        fallback = []
        
        # Use general questions from minimal bank
        if 'general' in self.question_bank:
            for level in ['entry', 'intermediate', 'senior', 'expert']:
                if level in self.question_bank['general']:
                    fallback.extend(self.question_bank['general'][level])
        
        # If somehow still empty, add ultra-basic questions
        if not fallback:
            fallback = [
                {
                    "question": "What is professional development?",
                    "options": {
                        "A": "Continuous learning and skill improvement",
                        "B": "Getting promoted",
                        "C": "Changing jobs",
                        "D": "Avoiding training"
                    },
                    "correct_answer": "A",
                    "explanation": "Professional development involves ongoing skill enhancement"
                },
                {
                    "question": "What is work-life balance?",
                    "options": {
                        "A": "Managing work and personal life effectively",
                        "B": "Working all the time",
                        "C": "Avoiding work",
                        "D": "Working from home only"
                    },
                    "correct_answer": "A",
                    "explanation": "Work-life balance optimizes both professional and personal well-being"
                }
            ]
        
        # Shuffle and return requested number
        random.shuffle(fallback)
        return fallback[:num_questions]
    
    # Remove the massive static question bank - no longer needed with API
    # The old _build_question_bank() method with 145+ questions is removed
    # API generates fresh questions dynamically based on actual user skills
                "entry": [
                    {
                        "question": "What is the correct way to create a list in Python?",
                        "options": {"A": "list = (1, 2, 3)", "B": "list = [1, 2, 3]", "C": "list = {1, 2, 3}", "D": "list = <1, 2, 3>"},
                        "correct_answer": "B",
                        "explanation": "Lists in Python are created using square brackets []"
                    },
                    {
                        "question": "Which keyword is used to define a function in Python?",
                        "options": {"A": "function", "B": "def", "C": "define", "D": "func"},
                        "correct_answer": "B",
                        "explanation": "Python uses 'def' keyword to define functions"
                    },
                    {
                        "question": "What is the output of: print(type(5.0))?",
                        "options": {"A": "<class 'int'>", "B": "<class 'float'>", "C": "<class 'str'>", "D": "<class 'decimal'>"},
                        "correct_answer": "B",
                        "explanation": "5.0 is a floating-point number in Python"
                    },
                    {
                        "question": "Which operator is used for exponentiation in Python?",
                        "options": {"A": "^", "B": "**", "C": "exp()", "D": "pow"},
                        "correct_answer": "B",
                        "explanation": "** is the exponentiation operator in Python"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is a decorator in Python?",
                        "options": {"A": "A function that modifies another function", "B": "A design pattern", "C": "A type of loop", "D": "A class method"},
                        "correct_answer": "A",
                        "explanation": "Decorators modify or enhance functions without changing their code"
                    },
                    {
                        "question": "What does list comprehension [x**2 for x in range(5)] produce?",
                        "options": {"A": "[0, 1, 4, 9, 16]", "B": "[1, 2, 3, 4, 5]", "C": "[0, 2, 4, 6, 8]", "D": "[1, 4, 9, 16, 25]"},
                        "correct_answer": "A",
                        "explanation": "Squares of 0,1,2,3,4 are 0,1,4,9,16"
                    },
                    {
                        "question": "What is the purpose of __init__ method?",
                        "options": {"A": "Destroy an object", "B": "Initialize object attributes", "C": "Call parent class", "D": "Create static methods"},
                        "correct_answer": "B",
                        "explanation": "__init__ is a constructor that initializes object attributes"
                    },
                    {
                        "question": "What does 'self' represent in a class method?",
                        "options": {"A": "The class itself", "B": "The instance of the class", "C": "A global variable", "D": "The parent class"},
                        "correct_answer": "B",
                        "explanation": "self refers to the instance of the class"
                    }
                ],
                "senior": [
                    {
                        "question": "What is the Global Interpreter Lock (GIL) in Python?",
                        "options": {"A": "A mutex preventing multiple threads from executing Python bytecode", "B": "A security feature", "C": "A memory manager", "D": "A syntax checker"},
                        "correct_answer": "A",
                        "explanation": "GIL is a mutex that protects access to Python objects"
                    },
                    {
                        "question": "What is the difference between __new__ and __init__?",
                        "options": {"A": "__new__ creates instance, __init__ initializes it", "B": "They are the same", "C": "__init__ creates, __new__ initializes", "D": "__new__ is for inheritance only"},
                        "correct_answer": "A",
                        "explanation": "__new__ creates the instance, __init__ initializes it"
                    },
                    {
                        "question": "What is a metaclass in Python?",
                        "options": {"A": "A class of a class", "B": "An abstract class", "C": "A parent class", "D": "A static class"},
                        "correct_answer": "A",
                        "explanation": "Metaclass is a class whose instances are classes"
                    }
                ],
                "expert": [
                    {
                        "question": "How does Python's garbage collection work?",
                        "options": {"A": "Reference counting with cycle detection", "B": "Mark and sweep only", "C": "Manual memory management", "D": "Automatic memory allocation"},
                        "correct_answer": "A",
                        "explanation": "Python uses reference counting with generational garbage collection for cycles"
                    },
                    {
                        "question": "What is the purpose of __slots__ in Python?",
                        "options": {"A": "Reduce memory overhead of objects", "B": "Create abstract methods", "C": "Define class variables", "D": "Implement interfaces"},
                        "correct_answer": "A",
                        "explanation": "__slots__ restricts instance attributes and reduces memory usage"
                    }
                ]
            },
            
            # JavaScript Questions
            "javascript": {
                "entry": [
                    {
                        "question": "How do you declare a variable in JavaScript (ES6+)?",
                        "options": {"A": "var x", "B": "let x or const x", "C": "int x", "D": "variable x"},
                        "correct_answer": "B",
                        "explanation": "ES6 introduced let and const for variable declaration"
                    },
                    {
                        "question": "What does === operator do in JavaScript?",
                        "options": {"A": "Assignment", "B": "Equality without type coercion", "C": "Greater than", "D": "Concatenation"},
                        "correct_answer": "B",
                        "explanation": "=== checks equality without type conversion"
                    },
                    {
                        "question": "Which method adds an element to the end of an array?",
                        "options": {"A": "push()", "B": "add()", "C": "append()", "D": "insert()"},
                        "correct_answer": "A",
                        "explanation": "push() adds elements to the end of an array"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is a closure in JavaScript?",
                        "options": {"A": "Function with access to outer scope", "B": "A loop construct", "C": "A class method", "D": "An event handler"},
                        "correct_answer": "A",
                        "explanation": "Closure is a function that remembers its outer scope"
                    },
                    {
                        "question": "What does the 'this' keyword refer to?",
                        "options": {"A": "The current object context", "B": "Global object always", "C": "Parent function", "D": "Window object only"},
                        "correct_answer": "A",
                        "explanation": "'this' refers to the object in current execution context"
                    },
                    {
                        "question": "What is event bubbling?",
                        "options": {"A": "Events propagate from child to parent", "B": "Creating events", "C": "Deleting events", "D": "Events fire twice"},
                        "correct_answer": "A",
                        "explanation": "Event bubbling is when events propagate up the DOM tree"
                    }
                ],
                "senior": [
                    {
                        "question": "What is the event loop in JavaScript?",
                        "options": {"A": "Mechanism for handling async operations", "B": "A for loop", "C": "Event listener", "D": "Error handler"},
                        "correct_answer": "A",
                        "explanation": "Event loop manages async callback execution"
                    },
                    {
                        "question": "What is the difference between call, apply, and bind?",
                        "options": {"A": "Different ways to set 'this' context", "B": "They are the same", "C": "call is async, apply is sync", "D": "bind creates classes"},
                        "correct_answer": "A",
                        "explanation": "All set 'this' context but call/apply invoke immediately, bind returns new function"
                    }
                ],
                "expert": [
                    {
                        "question": "How does JavaScript's prototype chain work?",
                        "options": {"A": "Objects inherit properties from prototypes", "B": "Classes extend each other", "C": "Functions call each other", "D": "Variables scope upward"},
                        "correct_answer": "A",
                        "explanation": "Prototype chain allows objects to inherit properties from prototypes"
                    }
                ]
            },
            
            # Django Questions
            "django": {
                "entry": [
                    {
                        "question": "What is Django?",
                        "options": {"A": "A Python web framework", "B": "A database", "C": "A JavaScript library", "D": "An operating system"},
                        "correct_answer": "A",
                        "explanation": "Django is a high-level Python web framework"
                    },
                    {
                        "question": "What command creates a new Django project?",
                        "options": {"A": "django-admin startproject", "B": "python new project", "C": "django create", "D": "npm init"},
                        "correct_answer": "A",
                        "explanation": "django-admin startproject creates a new Django project"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is an ORM in Django?",
                        "options": {"A": "Object-Relational Mapping for database operations", "B": "A security feature", "C": "A template engine", "D": "A routing system"},
                        "correct_answer": "A",
                        "explanation": "ORM maps Python objects to database tables"
                    },
                    {
                        "question": "What is the purpose of middleware in Django?",
                        "options": {"A": "Process requests/responses globally", "B": "Store data", "C": "Render templates", "D": "Handle URLs"},
                        "correct_answer": "A",
                        "explanation": "Middleware processes requests and responses at a global level"
                    }
                ],
                "senior": [
                    {
                        "question": "How does Django's signal system work?",
                        "options": {"A": "Decoupled applications can notify each other", "B": "Error handling", "C": "URL routing", "D": "Template rendering"},
                        "correct_answer": "A",
                        "explanation": "Signals allow decoupled applications to get notified of actions"
                    }
                ],
                "expert": [
                    {
                        "question": "How would you optimize Django querysets for performance?",
                        "options": {"A": "Use select_related and prefetch_related", "B": "Use raw SQL only", "C": "Disable ORM", "D": "Use multiple databases"},
                        "correct_answer": "A",
                        "explanation": "select_related and prefetch_related reduce database queries"
                    }
                ]
            },
            
            # React Questions
            "react": {
                "entry": [
                    {
                        "question": "What is React?",
                        "options": {"A": "A JavaScript library for building UIs", "B": "A database", "C": "A backend framework", "D": "A CSS framework"},
                        "correct_answer": "A",
                        "explanation": "React is a JavaScript library for building user interfaces"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What are React hooks?",
                        "options": {"A": "Functions to use state in functional components", "B": "Event handlers", "C": "CSS classes", "D": "Database queries"},
                        "correct_answer": "A",
                        "explanation": "Hooks allow state and lifecycle in functional components"
                    },
                    {
                        "question": "What is the Virtual DOM?",
                        "options": {"A": "Lightweight copy of the real DOM", "B": "Browser API", "C": "CSS framework", "D": "Database structure"},
                        "correct_answer": "A",
                        "explanation": "Virtual DOM is a programming concept where a virtual representation of UI is kept in memory"
                    }
                ],
                "senior": [
                    {
                        "question": "What is React's reconciliation algorithm?",
                        "options": {"A": "Algorithm to update the DOM efficiently", "B": "State management", "C": "Routing system", "D": "API calls"},
                        "correct_answer": "A",
                        "explanation": "Reconciliation determines which parts of the DOM need to be updated"
                    }
                ]
            },
            
            # SQL/Database Questions
            "sql": {
                "entry": [
                    {
                        "question": "What does SQL stand for?",
                        "options": {"A": "Structured Query Language", "B": "Simple Question Language", "C": "Standard Query List", "D": "System Query Logic"},
                        "correct_answer": "A",
                        "explanation": "SQL stands for Structured Query Language"
                    },
                    {
                        "question": "Which SQL command is used to retrieve data?",
                        "options": {"A": "SELECT", "B": "GET", "C": "FETCH", "D": "RETRIEVE"},
                        "correct_answer": "A",
                        "explanation": "SELECT is used to query and retrieve data"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is a foreign key?",
                        "options": {"A": "A field that links to primary key of another table", "B": "A unique identifier", "C": "An index", "D": "A data type"},
                        "correct_answer": "A",
                        "explanation": "Foreign key establishes relationships between tables"
                    },
                    {
                        "question": "What is normalization in databases?",
                        "options": {"A": "Organizing data to reduce redundancy", "B": "Backing up data", "C": "Encrypting data", "D": "Indexing tables"},
                        "correct_answer": "A",
                        "explanation": "Normalization reduces data redundancy and improves integrity"
                    }
                ],
                "senior": [
                    {
                        "question": "What is a database index?",
                        "options": {"A": "Data structure to speed up queries", "B": "Primary key", "C": "Table name", "D": "Column type"},
                        "correct_answer": "A",
                        "explanation": "Index improves query performance by creating data structures"
                    },
                    {
                        "question": "What is ACID in databases?",
                        "options": {"A": "Atomicity, Consistency, Isolation, Durability", "B": "A database type", "C": "A query language", "D": "A backup method"},
                        "correct_answer": "A",
                        "explanation": "ACID properties ensure reliable database transactions"
                    }
                ]
            },
            
            # General Programming
            "programming": {
                "entry": [
                    {
                        "question": "What is an algorithm?",
                        "options": {"A": "Step-by-step procedure to solve a problem", "B": "A programming language", "C": "A data type", "D": "A function"},
                        "correct_answer": "A",
                        "explanation": "Algorithm is a systematic procedure to solve a problem"
                    },
                    {
                        "question": "What does API stand for?",
                        "options": {"A": "Application Programming Interface", "B": "Advanced Program Integration", "C": "Automated Process Interface", "D": "Application Process Integration"},
                        "correct_answer": "A",
                        "explanation": "API allows different software to communicate"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is Object-Oriented Programming?",
                        "options": {"A": "Programming paradigm using objects and classes", "B": "Sequential programming", "C": "Functional programming", "D": "Low-level programming"},
                        "correct_answer": "A",
                        "explanation": "OOP organizes software design around data, or objects"
                    },
                    {
                        "question": "What is the time complexity of binary search?",
                        "options": {"A": "O(log n)", "B": "O(n)", "C": "O(n²)", "D": "O(1)"},
                        "correct_answer": "A",
                        "explanation": "Binary search divides the search space in half each time"
                    }
                ],
                "senior": [
                    {
                        "question": "What is a design pattern?",
                        "options": {"A": "Reusable solution to common software design problem", "B": "UI/UX design", "C": "Database schema", "D": "Coding style"},
                        "correct_answer": "A",
                        "explanation": "Design patterns are proven solutions to recurring design problems"
                    },
                    {
                        "question": "What is dependency injection?",
                        "options": {"A": "Providing dependencies from outside rather than creating them", "B": "Installing packages", "C": "Importing modules", "D": "Error handling"},
                        "correct_answer": "A",
                        "explanation": "DI is a technique where dependencies are provided externally"
                    }
                ]
            },
            
            # Git/Version Control
            "git": {
                "entry": [
                    {
                        "question": "What is Git?",
                        "options": {"A": "Distributed version control system", "B": "A programming language", "C": "A database", "D": "An IDE"},
                        "correct_answer": "A",
                        "explanation": "Git tracks changes in source code during development"
                    },
                    {
                        "question": "What command saves changes to local repository?",
                        "options": {"A": "git commit", "B": "git save", "C": "git push", "D": "git upload"},
                        "correct_answer": "A",
                        "explanation": "git commit saves changes to local repository"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is a merge conflict?",
                        "options": {"A": "When changes in different branches conflict", "B": "Syntax error", "C": "Network error", "D": "Permission error"},
                        "correct_answer": "A",
                        "explanation": "Merge conflicts occur when changes can't be automatically merged"
                    }
                ],
                "senior": [
                    {
                        "question": "What is git rebase?",
                        "options": {"A": "Reapply commits on top of another base", "B": "Delete commits", "C": "Create branches", "D": "Clone repository"},
                        "correct_answer": "A",
                        "explanation": "Rebase moves commits to a new base commit"
                    }
                ]
            },
            
            # Web Development
            "web": {
                "entry": [
                    {
                        "question": "What does HTML stand for?",
                        "options": {"A": "HyperText Markup Language", "B": "High Tech Modern Language", "C": "Home Tool Markup Language", "D": "Hyperlinks Text Markup Language"},
                        "correct_answer": "A",
                        "explanation": "HTML is the standard markup language for web pages"
                    },
                    {
                        "question": "What does CSS stand for?",
                        "options": {"A": "Cascading Style Sheets", "B": "Computer Style Sheets", "C": "Creative Style System", "D": "Colorful Style Sheets"},
                        "correct_answer": "A",
                        "explanation": "CSS describes how HTML elements are displayed"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is HTTPS?",
                        "options": {"A": "HTTP with encryption (SSL/TLS)", "B": "Fast HTTP", "C": "HTTP version 2", "D": "HTTP for servers"},
                        "correct_answer": "A",
                        "explanation": "HTTPS is HTTP protocol with encryption"
                    },
                    {
                        "question": "What are cookies in web development?",
                        "options": {"A": "Small data stored in browser", "B": "JavaScript files", "C": "CSS styles", "D": "HTML elements"},
                        "correct_answer": "A",
                        "explanation": "Cookies store user data in the browser"
                    }
                ],
                "senior": [
                    {
                        "question": "What is CORS?",
                        "options": {"A": "Cross-Origin Resource Sharing", "B": "Cookie Origin Security", "C": "Client Origin Request System", "D": "Code Organization Rules"},
                        "correct_answer": "A",
                        "explanation": "CORS allows controlled access to resources from different origins"
                    }
                ]
            },
            
            # ============= FINANCE & ACCOUNTING =============
            "finance": {
                "entry": [
                    {
                        "question": "What is a balance sheet?",
                        "options": {"A": "Financial statement showing assets, liabilities, and equity", "B": "A budget plan", "C": "An income statement", "D": "A tax return"},
                        "correct_answer": "A",
                        "explanation": "Balance sheet shows company's financial position at a specific point"
                    },
                    {
                        "question": "What does ROI stand for?",
                        "options": {"A": "Return on Investment", "B": "Rate of Interest", "C": "Revenue of Income", "D": "Risk of Investment"},
                        "correct_answer": "A",
                        "explanation": "ROI measures profitability of an investment"
                    },
                    {
                        "question": "What is accounts payable?",
                        "options": {"A": "Money a company owes to suppliers", "B": "Money customers owe to company", "C": "Employee salaries", "D": "Bank loans"},
                        "correct_answer": "A",
                        "explanation": "Accounts payable represents short-term obligations to creditors"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is the difference between FIFO and LIFO?",
                        "options": {"A": "Inventory valuation methods", "B": "Tax calculation methods", "C": "Depreciation methods", "D": "Accounting software"},
                        "correct_answer": "A",
                        "explanation": "FIFO (First In First Out) and LIFO (Last In First Out) are inventory accounting methods"
                    },
                    {
                        "question": "What is working capital?",
                        "options": {"A": "Current assets minus current liabilities", "B": "Total assets", "C": "Annual revenue", "D": "Profit margin"},
                        "correct_answer": "A",
                        "explanation": "Working capital measures short-term financial health"
                    },
                    {
                        "question": "What is depreciation?",
                        "options": {"A": "Systematic allocation of asset cost over its useful life", "B": "Decrease in sales", "C": "Loss of customers", "D": "Market downturn"},
                        "correct_answer": "A",
                        "explanation": "Depreciation spreads the cost of assets over time"
                    }
                ],
                "senior": [
                    {
                        "question": "What is the purpose of double-entry bookkeeping?",
                        "options": {"A": "Ensure accounting equation always balances", "B": "Record transactions twice for backup", "C": "Calculate taxes twice", "D": "Verify customer payments"},
                        "correct_answer": "A",
                        "explanation": "Double-entry system maintains accounting equation: Assets = Liabilities + Equity"
                    },
                    {
                        "question": "What is a cash flow statement used for?",
                        "options": {"A": "Track cash inflows and outflows", "B": "Calculate profit", "C": "List assets", "D": "Show liabilities"},
                        "correct_answer": "A",
                        "explanation": "Cash flow statement shows how cash moves in and out of business"
                    }
                ],
                "expert": [
                    {
                        "question": "What is EBITDA?",
                        "options": {"A": "Earnings Before Interest, Taxes, Depreciation, and Amortization", "B": "Equity Balance in Total Depreciation Assets", "C": "Expected Business Income Tax Deduction Amount", "D": "Electronic Banking International Transaction Data"},
                        "correct_answer": "A",
                        "explanation": "EBITDA measures operating performance excluding financing and accounting decisions"
                    }
                ]
            },
            
            "accounting": {
                "entry": [
                    {
                        "question": "What is a debit in accounting?",
                        "options": {"A": "An entry on the left side of an account", "B": "Money owed", "C": "A bank withdrawal", "D": "An expense only"},
                        "correct_answer": "A",
                        "explanation": "Debit is the left-side entry in double-entry bookkeeping"
                    },
                    {
                        "question": "What is the accounting equation?",
                        "options": {"A": "Assets = Liabilities + Equity", "B": "Revenue - Expenses = Profit", "C": "Assets + Liabilities = Equity", "D": "Income - Costs = Net Worth"},
                        "correct_answer": "A",
                        "explanation": "The fundamental accounting equation must always balance"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is accrual accounting?",
                        "options": {"A": "Recording revenue when earned and expenses when incurred", "B": "Recording only cash transactions", "C": "Yearly financial reporting", "D": "Tax calculation method"},
                        "correct_answer": "A",
                        "explanation": "Accrual accounting matches revenues with related expenses"
                    }
                ],
                "senior": [
                    {
                        "question": "What are Generally Accepted Accounting Principles (GAAP)?",
                        "options": {"A": "Standard accounting rules and practices", "B": "Government accounting procedures", "C": "Global audit practices", "D": "General accounting principles"},
                        "correct_answer": "A",
                        "explanation": "GAAP provides standardized accounting guidelines"
                    }
                ]
            },
            
            # ============= HEALTHCARE & MEDICAL =============
            "healthcare": {
                "entry": [
                    {
                        "question": "What does CPR stand for?",
                        "options": {"A": "Cardiopulmonary Resuscitation", "B": "Critical Patient Response", "C": "Cardiac Pressure Relief", "D": "Clinical Patient Recovery"},
                        "correct_answer": "A",
                        "explanation": "CPR is an emergency lifesaving procedure for cardiac arrest"
                    },
                    {
                        "question": "What is the normal human body temperature in Celsius?",
                        "options": {"A": "37°C", "B": "35°C", "C": "39°C", "D": "40°C"},
                        "correct_answer": "A",
                        "explanation": "Normal body temperature is approximately 37°C or 98.6°F"
                    },
                    {
                        "question": "What does BMI measure?",
                        "options": {"A": "Body Mass Index - weight relative to height", "B": "Blood Mineral Index", "C": "Basic Metabolic Indicator", "D": "Bone Mineral Index"},
                        "correct_answer": "A",
                        "explanation": "BMI is a measure of body fat based on height and weight"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is triage in healthcare?",
                        "options": {"A": "Prioritizing patients based on severity of condition", "B": "Patient registration process", "C": "Medical billing procedure", "D": "Discharge planning"},
                        "correct_answer": "A",
                        "explanation": "Triage determines treatment priority in emergency situations"
                    },
                    {
                        "question": "What is informed consent?",
                        "options": {"A": "Patient's agreement to treatment after understanding risks and benefits", "B": "Insurance approval", "C": "Hospital admission form", "D": "Medical record release"},
                        "correct_answer": "A",
                        "explanation": "Informed consent ensures patients understand and agree to medical procedures"
                    }
                ],
                "senior": [
                    {
                        "question": "What is evidence-based practice in healthcare?",
                        "options": {"A": "Using research evidence to guide clinical decisions", "B": "Following hospital policies", "C": "Learning from experience only", "D": "Using traditional methods"},
                        "correct_answer": "A",
                        "explanation": "Evidence-based practice integrates research with clinical expertise"
                    }
                ],
                "expert": [
                    {
                        "question": "What is pharmacokinetics?",
                        "options": {"A": "Study of how body processes drugs", "B": "Drug manufacturing process", "C": "Pharmacy management", "D": "Drug pricing strategy"},
                        "correct_answer": "A",
                        "explanation": "Pharmacokinetics studies absorption, distribution, metabolism, and excretion of drugs"
                    }
                ]
            },
            
            "nursing": {
                "entry": [
                    {
                        "question": "What are vital signs?",
                        "options": {"A": "Temperature, pulse, respiration, blood pressure", "B": "Patient symptoms", "C": "Lab results", "D": "Medical history"},
                        "correct_answer": "A",
                        "explanation": "Vital signs are basic measurements of body functions"
                    },
                    {
                        "question": "What does PPE stand for in healthcare?",
                        "options": {"A": "Personal Protective Equipment", "B": "Patient Protection Equipment", "C": "Professional Practice Evaluation", "D": "Primary Patient Examination"},
                        "correct_answer": "A",
                        "explanation": "PPE includes gloves, masks, gowns for infection control"
                    },
                    {
                        "question": "What is the purpose of hand hygiene?",
                        "options": {"A": "Prevent infection transmission", "B": "Keep hands soft", "C": "Hospital policy only", "D": "Patient comfort"},
                        "correct_answer": "A",
                        "explanation": "Hand hygiene is critical for preventing healthcare-associated infections"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is aseptic technique?",
                        "options": {"A": "Practices to prevent contamination and infection", "B": "Surgical procedure", "C": "Medication administration", "D": "Patient assessment method"},
                        "correct_answer": "A",
                        "explanation": "Aseptic technique maintains sterility and prevents infection"
                    },
                    {
                        "question": "What is the purpose of patient charting?",
                        "options": {"A": "Document care and communicate with healthcare team", "B": "Billing purposes only", "C": "Legal protection only", "D": "Hospital requirements"},
                        "correct_answer": "A",
                        "explanation": "Charting ensures continuity of care and legal documentation"
                    },
                    {
                        "question": "What does HIPAA protect?",
                        "options": {"A": "Patient health information privacy", "B": "Hospital profits", "C": "Insurance claims", "D": "Medical equipment"},
                        "correct_answer": "A",
                        "explanation": "HIPAA ensures confidentiality of patient health information"
                    }
                ],
                "senior": [
                    {
                        "question": "What is the nursing process?",
                        "options": {"A": "Assessment, Diagnosis, Planning, Implementation, Evaluation", "B": "Medication administration steps", "C": "Patient admission procedure", "D": "Documentation requirements"},
                        "correct_answer": "A",
                        "explanation": "The nursing process is a systematic approach to patient care"
                    },
                    {
                        "question": "What is critical thinking in nursing?",
                        "options": {"A": "Purposeful, goal-directed thinking for patient care decisions", "B": "Criticizing other nurses", "C": "Following protocols strictly", "D": "Documenting everything"},
                        "correct_answer": "A",
                        "explanation": "Critical thinking guides clinical judgment and decision-making"
                    }
                ]
            },
            
            # ============= MARKETING & SALES =============
            "marketing": {
                "entry": [
                    {
                        "question": "What are the 4 Ps of marketing?",
                        "options": {"A": "Product, Price, Place, Promotion", "B": "People, Process, Performance, Profit", "C": "Planning, Production, Pricing, Publicity", "D": "Position, Perception, Preference, Purchase"},
                        "correct_answer": "A",
                        "explanation": "The 4 Ps are the fundamental marketing mix elements"
                    },
                    {
                        "question": "What is a target market?",
                        "options": {"A": "Specific group of potential customers", "B": "Sales goal", "C": "Marketing budget", "D": "Advertising platform"},
                        "correct_answer": "A",
                        "explanation": "Target market is the intended audience for products or services"
                    },
                    {
                        "question": "What does B2B stand for?",
                        "options": {"A": "Business to Business", "B": "Brand to Brand", "C": "Buyer to Buyer", "D": "Business to Buyer"},
                        "correct_answer": "A",
                        "explanation": "B2B refers to transactions between businesses"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is brand equity?",
                        "options": {"A": "Value a brand adds to a product", "B": "Brand logo design", "C": "Brand ownership shares", "D": "Advertising budget"},
                        "correct_answer": "A",
                        "explanation": "Brand equity is the commercial value derived from consumer perception"
                    },
                    {
                        "question": "What is a call to action (CTA)?",
                        "options": {"A": "Prompt encouraging immediate response", "B": "Phone number", "C": "Email campaign", "D": "Social media post"},
                        "correct_answer": "A",
                        "explanation": "CTA drives audience to take a specific action"
                    },
                    {
                        "question": "What is SEO?",
                        "options": {"A": "Search Engine Optimization", "B": "Sales Engagement Online", "C": "Social Event Outreach", "D": "Strategic Email Operations"},
                        "correct_answer": "A",
                        "explanation": "SEO improves website visibility in search results"
                    }
                ],
                "senior": [
                    {
                        "question": "What is customer lifetime value (CLV)?",
                        "options": {"A": "Total revenue from a customer over relationship duration", "B": "Average purchase value", "C": "Customer satisfaction score", "D": "Marketing cost per customer"},
                        "correct_answer": "A",
                        "explanation": "CLV predicts net profit from entire customer relationship"
                    },
                    {
                        "question": "What is market segmentation?",
                        "options": {"A": "Dividing market into distinct groups of consumers", "B": "Creating product categories", "C": "Geographic expansion", "D": "Price differentiation"},
                        "correct_answer": "A",
                        "explanation": "Market segmentation groups customers with similar needs"
                    }
                ],
                "expert": [
                    {
                        "question": "What is the difference between positioning and differentiation?",
                        "options": {"A": "Positioning is perception in mind, differentiation is actual uniqueness", "B": "They are the same", "C": "Positioning is for products, differentiation for brands", "D": "Differentiation is cheaper than positioning"},
                        "correct_answer": "A",
                        "explanation": "Positioning focuses on perception while differentiation on actual unique features"
                    }
                ]
            },
            
            "sales": {
                "entry": [
                    {
                        "question": "What is a sales funnel?",
                        "options": {"A": "Process prospects go through to become customers", "B": "Sales team structure", "C": "Product catalog", "D": "Discount strategy"},
                        "correct_answer": "A",
                        "explanation": "Sales funnel represents the customer journey from awareness to purchase"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is objection handling?",
                        "options": {"A": "Addressing customer concerns during sales process", "B": "Rejecting bad leads", "C": "Defending product prices", "D": "Handling complaints"},
                        "correct_answer": "A",
                        "explanation": "Objection handling turns customer concerns into opportunities"
                    },
                    {
                        "question": "What does CRM stand for?",
                        "options": {"A": "Customer Relationship Management", "B": "Client Revenue Monitoring", "C": "Contact Record Management", "D": "Customer Retention Method"},
                        "correct_answer": "A",
                        "explanation": "CRM systems manage interactions with current and potential customers"
                    }
                ],
                "senior": [
                    {
                        "question": "What is consultative selling?",
                        "options": {"A": "Acting as advisor to identify customer needs", "B": "Selling consulting services", "C": "Group selling approach", "D": "Discounting strategy"},
                        "correct_answer": "A",
                        "explanation": "Consultative selling focuses on building relationships and understanding needs"
                    }
                ]
            },
            
            # ============= HUMAN RESOURCES =============
            "hr": {
                "entry": [
                    {
                        "question": "What is onboarding?",
                        "options": {"A": "Process of integrating new employees", "B": "Hiring process", "C": "Exit interview", "D": "Performance review"},
                        "correct_answer": "A",
                        "explanation": "Onboarding helps new hires adjust to their role and organization"
                    },
                    {
                        "question": "What is KPI in HR context?",
                        "options": {"A": "Key Performance Indicator", "B": "Knowledge Process Integration", "C": "Kinetic Performance Index", "D": "Key Personnel Information"},
                        "correct_answer": "A",
                        "explanation": "KPIs measure employee and organizational performance"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is employee retention?",
                        "options": {"A": "Ability to keep employees working for organization", "B": "Hiring more employees", "C": "Training programs", "D": "Salary structure"},
                        "correct_answer": "A",
                        "explanation": "Retention focuses on reducing employee turnover"
                    },
                    {
                        "question": "What is performance appraisal?",
                        "options": {"A": "Systematic evaluation of employee performance", "B": "Salary negotiation", "C": "Job description", "D": "Hiring interview"},
                        "correct_answer": "A",
                        "explanation": "Performance appraisal assesses employee contributions and development"
                    }
                ],
                "senior": [
                    {
                        "question": "What is talent management?",
                        "options": {"A": "Strategic approach to attract, develop, and retain talent", "B": "Entertainment industry management", "C": "Employee scheduling", "D": "Payroll processing"},
                        "correct_answer": "A",
                        "explanation": "Talent management ensures organization has the right people in right roles"
                    },
                    {
                        "question": "What is organizational culture?",
                        "options": {"A": "Shared values, beliefs, and practices of organization", "B": "Company logo and branding", "C": "Office layout", "D": "Dress code policy"},
                        "correct_answer": "A",
                        "explanation": "Organizational culture shapes behavior and environment"
                    }
                ]
            },
            
            # ============= EDUCATION & TEACHING =============
            "education": {
                "entry": [
                    {
                        "question": "What is differentiated instruction?",
                        "options": {"A": "Tailoring teaching to individual student needs", "B": "Teaching different subjects", "C": "Using different textbooks", "D": "Separating students by ability"},
                        "correct_answer": "A",
                        "explanation": "Differentiated instruction adapts teaching methods to diverse learners"
                    },
                    {
                        "question": "What is formative assessment?",
                        "options": {"A": "Ongoing feedback during learning process", "B": "Final exam", "C": "Entrance test", "D": "Graduation requirement"},
                        "correct_answer": "A",
                        "explanation": "Formative assessment monitors student learning to provide feedback"
                    },
                    {
                        "question": "What is a learning objective?",
                        "options": {"A": "Clear statement of what students should know or do", "B": "Course textbook", "C": "Classroom rule", "D": "Grading policy"},
                        "correct_answer": "A",
                        "explanation": "Learning objectives guide instruction and assessment"
                    },
                    {
                        "question": "What does IEP stand for?",
                        "options": {"A": "Individualized Education Program", "B": "Integrated Educational Plan", "C": "Initial Education Process", "D": "Instructional Evaluation Procedure"},
                        "correct_answer": "A",
                        "explanation": "IEP is a customized plan for students with special needs"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is Bloom's Taxonomy?",
                        "options": {"A": "Classification of learning objectives by complexity", "B": "Student grading system", "C": "Teaching method", "D": "School management framework"},
                        "correct_answer": "A",
                        "explanation": "Bloom's Taxonomy categorizes cognitive skills from basic to advanced"
                    },
                    {
                        "question": "What is scaffolding in education?",
                        "options": {"A": "Providing temporary support until students can work independently", "B": "Building structure for schools", "C": "Creating lesson plans", "D": "Organizing curriculum"},
                        "correct_answer": "A",
                        "explanation": "Scaffolding gradually releases responsibility to students"
                    },
                    {
                        "question": "What is cooperative learning?",
                        "options": {"A": "Students working together in small groups", "B": "Teacher lecturing", "C": "Individual assignments", "D": "Online learning"},
                        "correct_answer": "A",
                        "explanation": "Cooperative learning promotes peer interaction and collaboration"
                    },
                    {
                        "question": "What is summative assessment?",
                        "options": {"A": "Evaluation of learning at end of period", "B": "Daily quizzes", "C": "Classroom participation", "D": "Homework assignments"},
                        "correct_answer": "A",
                        "explanation": "Summative assessment measures overall achievement"
                    }
                ],
                "senior": [
                    {
                        "question": "What is metacognition?",
                        "options": {"A": "Thinking about one's own thinking and learning", "B": "Advanced mathematics", "C": "Memory techniques", "D": "Critical thinking skills"},
                        "correct_answer": "A",
                        "explanation": "Metacognition involves awareness and regulation of one's learning process"
                    },
                    {
                        "question": "What is backward design in curriculum planning?",
                        "options": {"A": "Starting with desired outcomes and working backward", "B": "Reviewing last year's curriculum", "C": "Teaching in reverse order", "D": "Retroactive assessment"},
                        "correct_answer": "A",
                        "explanation": "Backward design begins with end goals to plan instruction"
                    }
                ]
            },
            
            # ============= HOSPITALITY & TOURISM =============
            "hospitality": {
                "entry": [
                    {
                        "question": "What does F&B stand for in hospitality?",
                        "options": {"A": "Food and Beverage", "B": "Front and Back", "C": "Facilities and Building", "D": "Finance and Budget"},
                        "correct_answer": "A",
                        "explanation": "F&B refers to food and beverage services in hotels and restaurants"
                    },
                    {
                        "question": "What is the role of a concierge?",
                        "options": {"A": "Assist guests with services and recommendations", "B": "Clean rooms", "C": "Prepare food", "D": "Handle finances"},
                        "correct_answer": "A",
                        "explanation": "Concierge provides personalized guest services and local information"
                    },
                    {
                        "question": "What is check-in time?",
                        "options": {"A": "Time when guests can access their rooms", "B": "Time employees start work", "C": "Restaurant opening time", "D": "Payment processing time"},
                        "correct_answer": "A",
                        "explanation": "Check-in is when room assignment and key distribution occur"
                    },
                    {
                        "question": "What is upselling in hospitality?",
                        "options": {"A": "Encouraging guests to upgrade services", "B": "Raising prices", "C": "Selling merchandise", "D": "Increasing staff"},
                        "correct_answer": "A",
                        "explanation": "Upselling offers premium options to enhance guest experience and revenue"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is occupancy rate?",
                        "options": {"A": "Percentage of available rooms occupied", "B": "Hotel guest capacity", "C": "Staff to guest ratio", "D": "Room cleaning speed"},
                        "correct_answer": "A",
                        "explanation": "Occupancy rate measures hotel utilization efficiency"
                    },
                    {
                        "question": "What is RevPAR?",
                        "options": {"A": "Revenue Per Available Room", "B": "Revenue Per Actual Reservation", "C": "Room Evaluation Performance Analysis Report", "D": "Registered Visitor Per Area Room"},
                        "correct_answer": "A",
                        "explanation": "RevPAR is key hotel performance metric"
                    },
                    {
                        "question": "What is ADR in hospitality?",
                        "options": {"A": "Average Daily Rate", "B": "Annual Discount Rate", "C": "Adjusted Daily Revenue", "D": "Advance Deposit Requirement"},
                        "correct_answer": "A",
                        "explanation": "ADR is average rental income per occupied room"
                    },
                    {
                        "question": "What is turndown service?",
                        "options": {"A": "Evening service preparing room for sleep", "B": "Rejecting reservations", "C": "Reducing room temperature", "D": "Declining service requests"},
                        "correct_answer": "A",
                        "explanation": "Turndown service prepares room in the evening with amenities"
                    }
                ],
                "senior": [
                    {
                        "question": "What is yield management in hospitality?",
                        "options": {"A": "Pricing strategy to maximize revenue", "B": "Food waste reduction", "C": "Employee productivity", "D": "Guest satisfaction measurement"},
                        "correct_answer": "A",
                        "explanation": "Yield management optimizes pricing based on demand"
                    },
                    {
                        "question": "What is a GDS in hotel industry?",
                        "options": {"A": "Global Distribution System for bookings", "B": "Guest Data Security", "C": "General Dining Service", "D": "Group Discount System"},
                        "correct_answer": "A",
                        "explanation": "GDS connects hotels with travel agents and booking platforms"
                    }
                ]
            },
            
            # ============= CONSTRUCTION & ENGINEERING =============
            "construction": {
                "entry": [
                    {
                        "question": "What is a blueprint?",
                        "options": {"A": "Technical drawing of building plans", "B": "Budget document", "C": "Safety manual", "D": "Material list"},
                        "correct_answer": "A",
                        "explanation": "Blueprint is a detailed architectural or engineering drawing"
                    },
                    {
                        "question": "What does PPE stand for in construction?",
                        "options": {"A": "Personal Protective Equipment", "B": "Project Planning Estimate", "C": "Plumbing and Pipe Engineering", "D": "Primary Project Evaluation"},
                        "correct_answer": "A",
                        "explanation": "PPE includes safety gear like helmets, gloves, and boots"
                    },
                    {
                        "question": "What is the primary purpose of a foundation?",
                        "options": {"A": "Support structure and distribute weight", "B": "Prevent water damage only", "C": "Aesthetic appearance", "D": "Storage space"},
                        "correct_answer": "A",
                        "explanation": "Foundation transfers building load to the ground safely"
                    },
                    {
                        "question": "What is rebar used for?",
                        "options": {"A": "Reinforce concrete structures", "B": "Connect wooden beams", "C": "Electrical wiring", "D": "Plumbing pipes"},
                        "correct_answer": "A",
                        "explanation": "Rebar (reinforcing bar) strengthens concrete against tension"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is a load-bearing wall?",
                        "options": {"A": "Wall that supports weight from above", "B": "Decorative wall", "C": "External wall only", "D": "Foundation wall"},
                        "correct_answer": "A",
                        "explanation": "Load-bearing walls support structural weight and cannot be easily removed"
                    },
                    {
                        "question": "What is a Bill of Quantities (BOQ)?",
                        "options": {"A": "Document listing materials and labor quantities", "B": "Invoice", "C": "Building permit", "D": "Safety checklist"},
                        "correct_answer": "A",
                        "explanation": "BOQ details all materials and work required for construction"
                    },
                    {
                        "question": "What is the purpose of a site survey?",
                        "options": {"A": "Assess land conditions before construction", "B": "Count workers", "C": "Safety inspection", "D": "Customer satisfaction check"},
                        "correct_answer": "A",
                        "explanation": "Site survey evaluates terrain, boundaries, and conditions"
                    },
                    {
                        "question": "What does OSHA regulate?",
                        "options": {"A": "Workplace safety and health standards", "B": "Building permits", "C": "Construction prices", "D": "Material quality"},
                        "correct_answer": "A",
                        "explanation": "OSHA ensures safe and healthy working conditions"
                    }
                ],
                "senior": [
                    {
                        "question": "What is the critical path in project management?",
                        "options": {"A": "Longest sequence of dependent tasks determining project duration", "B": "Main entrance route", "C": "Most expensive tasks", "D": "Safety procedures"},
                        "correct_answer": "A",
                        "explanation": "Critical path determines minimum time needed to complete project"
                    },
                    {
                        "question": "What is value engineering?",
                        "options": {"A": "Optimizing project function while reducing costs", "B": "Appraising property", "C": "Structural analysis", "D": "Cost estimation"},
                        "correct_answer": "A",
                        "explanation": "Value engineering improves value through function analysis"
                    }
                ]
            },
            
            # ============= CUSTOMER SERVICE =============
            "customer_service": {
                "entry": [
                    {
                        "question": "What is active listening?",
                        "options": {"A": "Fully concentrating and understanding customer's message", "B": "Talking to customers", "C": "Recording conversations", "D": "Following scripts"},
                        "correct_answer": "A",
                        "explanation": "Active listening involves full attention and understanding customer needs"
                    },
                    {
                        "question": "What does empathy mean in customer service?",
                        "options": {"A": "Understanding and sharing customer's feelings", "B": "Agreeing with every customer", "C": "Offering discounts", "D": "Apologizing repeatedly"},
                        "correct_answer": "A",
                        "explanation": "Empathy shows customers you understand their perspective"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is service recovery?",
                        "options": {"A": "Actions taken to fix service failures", "B": "Restarting computer systems", "C": "Finding lost items", "D": "Backup procedures"},
                        "correct_answer": "A",
                        "explanation": "Service recovery aims to turn dissatisfied customers into satisfied ones"
                    },
                    {
                        "question": "What is first call resolution (FCR)?",
                        "options": {"A": "Resolving customer issue in first contact", "B": "Answering phone quickly", "C": "First customer of the day", "D": "Priority customer service"},
                        "correct_answer": "A",
                        "explanation": "FCR measures efficiency in solving problems without follow-ups"
                    }
                ],
                "senior": [
                    {
                        "question": "What is the service profit chain?",
                        "options": {"A": "Link between employee satisfaction, customer satisfaction, and profitability", "B": "Pricing strategy", "C": "Sales commission structure", "D": "Profit margin calculation"},
                        "correct_answer": "A",
                        "explanation": "Service profit chain shows how employee satisfaction drives customer loyalty and profits"
                    }
                ]
            },
            
            # ============= LOGISTICS & SUPPLY CHAIN =============
            "logistics": {
                "entry": [
                    {
                        "question": "What is inventory?",
                        "options": {"A": "Stock of goods and materials", "B": "Sales report", "C": "Customer list", "D": "Shipping containers"},
                        "correct_answer": "A",
                        "explanation": "Inventory represents goods available for sale or use"
                    },
                    {
                        "question": "What does FOB stand for?",
                        "options": {"A": "Free on Board", "B": "Freight or Budget", "C": "Full Order Batch", "D": "Forward Operating Base"},
                        "correct_answer": "A",
                        "explanation": "FOB indicates when ownership and liability transfer in shipping"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is Just-in-Time (JIT) inventory?",
                        "options": {"A": "System where materials arrive exactly when needed", "B": "Emergency stock", "C": "Bulk ordering", "D": "Long-term storage"},
                        "correct_answer": "A",
                        "explanation": "JIT minimizes inventory by receiving goods only as needed"
                    },
                    {
                        "question": "What is the supply chain?",
                        "options": {"A": "Network from raw materials to end customer", "B": "Delivery trucks", "C": "Warehouse layout", "D": "Product catalog"},
                        "correct_answer": "A",
                        "explanation": "Supply chain includes all steps from production to delivery"
                    }
                ],
                "senior": [
                    {
                        "question": "What is the bullwhip effect?",
                        "options": {"A": "Amplification of demand variability up the supply chain", "B": "Fast delivery method", "C": "Inventory damage", "D": "Price fluctuation"},
                        "correct_answer": "A",
                        "explanation": "Bullwhip effect shows how small demand changes cause larger supply chain fluctuations"
                    }
                ]
            },
            
            # ============= GENERAL BUSINESS & MANAGEMENT =============
            "management": {
                "entry": [
                    {
                        "question": "What is delegation?",
                        "options": {"A": "Assigning tasks and authority to others", "B": "Attending conferences", "C": "Making all decisions", "D": "Ignoring problems"},
                        "correct_answer": "A",
                        "explanation": "Delegation empowers team members and distributes workload"
                    },
                    {
                        "question": "What is a SWOT analysis?",
                        "options": {"A": "Analysis of Strengths, Weaknesses, Opportunities, Threats", "B": "Sales workflow optimization tool", "C": "Software testing method", "D": "Stock market analysis"},
                        "correct_answer": "A",
                        "explanation": "SWOT analyzes internal and external factors affecting organization"
                    }
                ],
                "intermediate": [
                    {
                        "question": "What is strategic planning?",
                        "options": {"A": "Long-term organizational direction and goal setting", "B": "Daily task scheduling", "C": "Budget allocation", "D": "Event planning"},
                        "correct_answer": "A",
                        "explanation": "Strategic planning defines organization's future direction and priorities"
                    },
                    {
                        "question": "What is change management?",
                        "options": {"A": "Process of transitioning organization to new methods", "B": "Handling petty cash", "C": "Currency exchange", "D": "Updating software"},
                        "correct_answer": "A",
                        "explanation": "Change management helps organizations adapt to new processes or structures"
                    }
                ],
                "senior": [
                    {
                        "question": "What is transformational leadership?",
                        "options": {"A": "Leadership that inspires and motivates toward shared vision", "B": "Changing job positions", "C": "Restructuring organization", "D": "Training new managers"},
                        "correct_answer": "A",
                        "explanation": "Transformational leaders inspire teams to exceed expectations"
                    }
                ]
            }
        }
    
    def _get_dynamic_questions(self, skills: str, experience_level: str, num_questions: int = 10) -> List[Dict[str, Any]]:
        """
        Generate dynamic questions based on user skills and experience level across ALL industries
        Randomly selects questions to avoid repetition
        """
        # Parse user skills - normalize and extract keywords
        user_skills = [skill.strip().lower() for skill in skills.split(',') if skill.strip()]
        
        # Map experience level
        level_map = {
            'entry': 'entry',
            'intermediate': 'intermediate',
            'senior': 'senior',
            'expert': 'expert',
            '': 'intermediate'  # Default
        }
        level = level_map.get(experience_level.lower() if experience_level else '', 'intermediate')
        
        # Collect relevant questions
        available_questions = []
        matched_skills = []
        
        # Enhanced skill matching - match user skills with question bank categories
        skill_category_map = {
            # Technology
            'python': ['python', 'django', 'flask', 'programming', 'coding', 'software', 'developer'],
            'javascript': ['javascript', 'js', 'node', 'react', 'angular', 'vue', 'web', 'frontend', 'backend', 'fullstack'],
            'django': ['django', 'python', 'web', 'backend', 'framework'],
            'react': ['react', 'frontend', 'ui', 'javascript', 'web'],
            'sql': ['sql', 'database', 'data', 'query', 'mysql', 'postgresql', 'oracle'],
            'programming': ['programming', 'coding', 'software', 'development', 'developer', 'engineer', 'tech'],
            'git': ['git', 'version', 'control', 'github', 'gitlab', 'devops', 'scm'],
            'web': ['web', 'html', 'css', 'internet', 'website', 'frontend', 'http'],
            
            # Finance & Accounting
            'finance': ['finance', 'financial', 'banking', 'investment', 'money', 'capital', 'trading', 'stock', 'budget'],
            'accounting': ['accounting', 'accountant', 'bookkeeping', 'ledger', 'audit', 'tax', 'payroll', 'gaap'],
            
            # Healthcare
            'healthcare': ['healthcare', 'medical', 'health', 'hospital', 'clinic', 'patient'],
            'nursing': ['nursing', 'nurse', 'patient care', 'clinical', 'ward', 'rn', 'lpn'],
            
            # Marketing & Sales
            'marketing': ['marketing', 'branding', 'advertising', 'promotion', 'digital marketing', 'seo', 'content', 'brand', 'campaign'],
            'sales': ['sales', 'selling', 'business development', 'account', 'client', 'revenue', 'crm'],
            
            # Human Resources
            'hr': ['hr', 'human resource', 'recruitment', 'hiring', 'talent', 'employee', 'personnel', 'payroll', 'recruiting'],
            
            # Education
            'education': ['education', 'teaching', 'teacher', 'training', 'instructor', 'tutor', 'academic', 'school', 'classroom', 'curriculum'],
            
            # Hospitality & Tourism
            'hospitality': ['hospitality', 'hotel', 'restaurant', 'tourism', 'guest', 'f&b', 'food', 'beverage', 'housekeeping'],
            
            # Construction & Engineering  
            'construction': ['construction', 'building', 'civil', 'engineering', 'contractor', 'architecture', 'site', 'blueprint', 'safety'],
            
            # Customer Service
            'customer_service': ['customer service', 'support', 'help desk', 'client service', 'call center', 'customer care', 'service desk'],
            
            # Logistics & Supply Chain
            'logistics': ['logistics', 'supply chain', 'warehouse', 'inventory', 'shipping', 'transportation', 'distribution', 'procurement'],
            
            # General Management
            'management': ['management', 'manager', 'leadership', 'administration', 'supervisor', 'executive', 'director', 'business']
        }
        
        # Match user skills with question bank categories
        for user_skill in user_skills:
            for category, keywords in skill_category_map.items():
                # Check if any keyword matches the user skill
                if any(keyword in user_skill for keyword in keywords) or any(user_skill in keyword for keyword in keywords):
                    if category in self.question_bank and category not in matched_skills:
                        matched_skills.append(category)
                        # Add questions from this category at the appropriate level
                        if level in self.question_bank[category]:
                            available_questions.extend(self.question_bank[category][level])
        
        # If no specific skill match found, use broader categories based on common keywords
        if not available_questions:
            print(f"INFO: No exact skill match. Using general questions based on keywords in: {skills}")
            
            # Try to infer industry from skills text
            skills_lower = skills.lower()
            
            # Check for industry keywords in skills text
            if any(word in skills_lower for word in ['business', 'management', 'admin', 'office']):
                if 'management' in self.question_bank and level in self.question_bank['management']:
                    available_questions.extend(self.question_bank['management'][level])
            
            if any(word in skills_lower for word in ['communication', 'people', 'customer', 'service', 'support']):
                if 'customer_service' in self.question_bank and level in self.question_bank['customer_service']:
                    available_questions.extend(self.question_bank['customer_service'][level])
            
            # If still nothing, use programming as general fallback
            if not available_questions and 'programming' in self.question_bank and level in self.question_bank['programming']:
                available_questions.extend(self.question_bank['programming'][level])
        
        # If still not enough questions, add from adjacent difficulty levels
        if len(available_questions) < num_questions and matched_skills:
            level_order = ['entry', 'intermediate', 'senior', 'expert']
            current_idx = level_order.index(level)
            
            # Add from next level
            if current_idx < len(level_order) - 1:
                next_level = level_order[current_idx + 1]
                for category in matched_skills:
                    if next_level in self.question_bank[category]:
                        available_questions.extend(self.question_bank[category][next_level])
            
            # Add from previous level if still need more
            if current_idx > 0 and len(available_questions) < num_questions:
                prev_level = level_order[current_idx - 1]
                for category in matched_skills:
                    if prev_level in self.question_bank[category]:
                        available_questions.extend(self.question_bank[category][prev_level])
        
        # If still not enough, add questions from all categories at current level (but prioritize non-tech)
        if len(available_questions) < num_questions:
            # Determine if user is tech or non-tech to provide better fallback
            tech_categories = ['python', 'javascript', 'django', 'react', 'sql', 'programming', 'git', 'web']
            non_tech_categories = [cat for cat in self.question_bank.keys() if cat not in tech_categories]
            
            is_tech_user = any(cat in matched_skills for cat in tech_categories)
            
            # Prioritize related categories for fallback
            fallback_categories = tech_categories if is_tech_user else non_tech_categories
            
            for category in fallback_categories:
                if len(available_questions) >= num_questions:
                    break
                if category not in matched_skills and level in self.question_bank.get(category, {}):
                    available_questions.extend(self.question_bank[category][level])
        
        # Remove duplicates based on question text
        seen = set()
        unique_questions = []
        for q in available_questions:
            if q['question'] not in seen:
                seen.add(q['question'])
                unique_questions.append(q)
        
        # Randomly shuffle and select required number
        random.shuffle(unique_questions)
        selected = unique_questions[:num_questions]
        
        # If still not enough, add general fallback questions
        if len(selected) < num_questions:
            fallback = self._get_fallback_questions("", num_questions - len(selected))
            selected.extend(fallback)
        
        print(f"INFO: Generated {len(selected)} questions from categories: {matched_skills if matched_skills else 'general/fallback'}")
        return selected[:num_questions]
