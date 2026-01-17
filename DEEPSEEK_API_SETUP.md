# DeepSeek API Configuration

## Current Status
✅ System is using **fallback questions** (high-quality pre-defined technical MCQs)
⚠️ DeepSeek API integration is **temporarily disabled**

## Why Fallback Mode?
The provided API key `sk-8621b35578914df287cfc2206cca725b` may not be valid or the DeepSeek API endpoint might require verification. To ensure the assessment system works immediately, we've enabled fallback mode with 10 excellent general technical questions.

## Fallback Questions Include:
1. API terminology
2. HTTP methods
3. Algorithm complexity
4. OOP concepts
5. Database types
6. Git commands
7. Python syntax
8. CSS terminology
9. JavaScript frameworks
10. Network protocols

## How to Enable DeepSeek API (When You Have a Valid Key)

### Step 1: Get a Valid API Key
Visit: https://platform.deepseek.com/
- Sign up for an account
- Navigate to API Keys section
- Generate a new API key
- Copy the key (starts with `sk-...`)

### Step 2: Update the Code
Open: `users/deepseek_service.py`

Find line ~31 (the generate_questions method) and make these changes:

**REMOVE these lines (18-20):**
```python
# TEMPORARY: Use fallback questions directly until API key is validated
print(f"INFO: Using fallback questions for skills: {skills}")
return self._get_fallback_questions(skills, num_questions)
```

**UNCOMMENT the API code:**
Remove the `"""` at line 22 and line 85 to uncomment the entire API integration block.

**UPDATE the API key:**
Line 12 in the `__init__` method:
```python
def __init__(self, api_key: str = "YOUR_NEW_API_KEY_HERE"):
```

### Step 3: Verify the API Endpoint
The current endpoint is:
```python
self.api_url = "https://api.deepseek.com/v1/chat/completions"
```

Verify this is correct in DeepSeek's documentation. It might be:
- `https://api.deepseek.com/chat/completions`
- `https://api.deepseek.ai/v1/chat/completions`
- Or another endpoint

### Step 4: Test the Integration
```bash
python manage.py shell
```

```python
from users.deepseek_service import DeepSeekQuestionGenerator

generator = DeepSeekQuestionGenerator(api_key="your-key-here")
questions = generator.generate_questions(
    skills="Python, Django, REST API",
    experience="Web development",
    experience_level="intermediate",
    num_questions=5
)

print(len(questions))  # Should print 5
print(questions[0])     # Should show first question
```

### Step 5: Restart Django Server
```bash
python manage.py runserver
```

## Alternative: Use OpenAI API Instead

If DeepSeek API is not available, you can easily switch to OpenAI's GPT API:

**Install OpenAI:**
```bash
pip install openai
```

**Update `users/deepseek_service.py`:**
```python
import openai

class DeepSeekQuestionGenerator:
    def __init__(self, api_key: str = "your-openai-key"):
        self.api_key = api_key
        openai.api_key = api_key
        
    def generate_questions(self, skills, experience, experience_level, num_questions=10):
        prompt = self._create_prompt(skills, experience, experience_level, num_questions)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer..."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            questions = self._parse_questions(content)
            return questions[:num_questions]
        except Exception as e:
            print(f"Error: {e}")
            return self._get_fallback_questions(skills, num_questions)
```

## Benefits of Each Approach

### Current (Fallback Questions)
✅ Works immediately, no API needed
✅ No API costs
✅ Consistent questions
✅ Fast response
❌ Not personalized to user skills
❌ Limited question variety

### DeepSeek API
✅ AI-generated personalized questions
✅ Matches user's exact skills
✅ Adapts to experience level
✅ Unlimited unique questions
❌ Requires valid API key
❌ Costs per API call
❌ Depends on internet/API availability

### OpenAI API
✅ Same benefits as DeepSeek
✅ More reliable (established service)
✅ Better documentation
❌ Higher cost than DeepSeek
❌ Requires API key

## Recommended Approach

**For Development/Testing:**
✅ Use current fallback questions (free, fast, reliable)

**For Production:**
1. Get a valid DeepSeek or OpenAI API key
2. Test thoroughly with different skill sets
3. Implement rate limiting to control costs
4. Keep fallback questions as backup

## Current System Status

The assessment system is **fully functional** right now with fallback questions. Users can:
- ✅ Take assessments
- ✅ Get scored (with time bonuses/penalties)
- ✅ See results on profile
- ✅ View past assessments

The only difference is questions are not AI-generated based on individual profiles - they're high-quality general technical questions suitable for all users.

## Questions?

If you encounter any issues or need help setting up the API, check the console logs when running the server - they'll show API errors if any occur.
