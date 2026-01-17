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
        self.question_bank = self._build_question_bank()
        
    def generate_questions(self, skills: str, experience: str, experience_level: str, num_questions: int = 10) -> List[Dict[str, Any]]:
        """
        Generate MCQ questions based on user profile
        
        Args:
            skills: Comma-separated skills
            experience: User's experience text
            experience_level: entry/intermediate/senior/expert
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries with question, options, and correct answer
        """
        
        # Use dynamic question selection based on user profile
        print(f"INFO: Generating questions for skills: {skills}, level: {experience_level}")
        return self._get_dynamic_questions(skills, experience_level, num_questions)
        
        # Original API code (commented out until valid API key is provided)
        """
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
                            "content": "You are an expert technical interviewer who creates precise, relevant MCQ questions for skill assessment. Always respond with valid JSON only."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse the JSON response
                questions = self._parse_questions(content)
                if questions and len(questions) > 0:
                    return questions[:num_questions]  # Ensure we return exactly num_questions
                else:
                    print("DeepSeek API returned no valid questions, using fallback")
                    return self._get_fallback_questions(skills, num_questions)
            else:
                print(f"DeepSeek API Error: {response.status_code} - {response.text}")
                return self._get_fallback_questions(skills, num_questions)
                
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return self._get_fallback_questions(skills, num_questions)
        """
    
    def _create_prompt(self, skills: str, experience: str, experience_level: str, num_questions: int) -> str:
        """Create a detailed prompt for question generation"""
        
        difficulty_mapping = {
            'entry': 'beginner to intermediate',
            'intermediate': 'intermediate',
            'senior': 'intermediate to advanced',
            'expert': 'advanced'
        }
        difficulty = difficulty_mapping.get(experience_level, 'intermediate')
        
        prompt = f"""Generate {num_questions} multiple-choice questions for a technical assessment.

User Profile:
- Skills: {skills or 'General IT/Programming'}
- Experience Level: {experience_level or 'intermediate'}
- Experience: {experience[:200] if experience else 'General software development'}

Requirements:
1. Questions should be at {difficulty} difficulty level
2. Focus primarily on the listed skills
3. Include practical scenario-based questions
4. Each question must have exactly 4 options (A, B, C, D)
5. Only ONE option should be correct
6. Questions should be clear and unambiguous

Response Format (MUST be valid JSON):
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

Generate exactly {num_questions} questions and respond ONLY with the JSON object."""
        
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
    
    def _build_question_bank(self) -> Dict[str, Dict[str, List[Dict]]]:
        """Build comprehensive question bank organized by skill and difficulty"""
        return {
            # Python Questions
            "python": {
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
            }
        }
    
    def _get_dynamic_questions(self, skills: str, experience_level: str, num_questions: int = 10) -> List[Dict[str, Any]]:
        """
        Generate dynamic questions based on user skills and experience level
        Randomly selects questions to avoid repetition
        """
        # Parse user skills
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
        
        # Match user skills with question bank
        for skill in user_skills:
            for bank_skill in self.question_bank.keys():
                if skill in bank_skill or bank_skill in skill:
                    if level in self.question_bank[bank_skill]:
                        available_questions.extend(self.question_bank[bank_skill][level])
        
        # If no specific skill match, use general programming questions
        if not available_questions:
            if 'programming' in self.question_bank and level in self.question_bank['programming']:
                available_questions.extend(self.question_bank['programming'][level])
            
            # Add web questions as general fallback
            if 'web' in self.question_bank and level in self.question_bank['web']:
                available_questions.extend(self.question_bank['web'][level])
        
        # If still not enough, add questions from adjacent difficulty levels
        if len(available_questions) < num_questions:
            level_order = ['entry', 'intermediate', 'senior', 'expert']
            current_idx = level_order.index(level)
            
            # Add from next level
            if current_idx < len(level_order) - 1:
                next_level = level_order[current_idx + 1]
                for skill_key in self.question_bank.keys():
                    if next_level in self.question_bank[skill_key]:
                        available_questions.extend(self.question_bank[skill_key][next_level])
            
            # Add from previous level
            if current_idx > 0 and len(available_questions) < num_questions:
                prev_level = level_order[current_idx - 1]
                for skill_key in self.question_bank.keys():
                    if prev_level in self.question_bank[skill_key]:
                        available_questions.extend(self.question_bank[skill_key][prev_level])
        
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
        
        return selected[:num_questions]
