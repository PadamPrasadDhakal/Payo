# Dynamic Assessment System - Payo

## Overview
The Dynamic Assessment System uses DeepSeek AI to generate personalized MCQ questions based on each user's skills and experience level. The system includes real-time scoring with time-based bonuses/penalties.

## Features

### 1. **AI-Powered Question Generation**
- Uses DeepSeek API to create personalized questions
- Questions match user's skills (from profile)
- Difficulty adapts to experience level (entry/intermediate/senior/expert)
- 10 questions per assessment

### 2. **Smart Scoring System**
- **Base Score**: Correct answers / Total questions × 100
- **Time Multiplier**:
  - Fast completion (<30s per question): +10% bonus
  - Slow completion (>60s per question): -10% penalty
- **Wrong Answer Penalty**: -5 points per wrong answer
- Final score capped between 0-100

### 3. **Real-time Timer**
- Tracks time elapsed during assessment
- Displayed in top-right corner
- Used for score calculation

### 4. **Grade System**
- A+ : 90-100%
- A  : 80-89%
- B  : 70-79%
- C  : 60-69%
- D  : 50-59%
- F  : Below 50%

## How It Works

### User Flow
1. User navigates to `/assessments/`
2. Clicks "Start Assessment Now"
3. System generates 10 questions based on user profile
4. User answers questions (timer running)
5. User submits assessment
6. System calculates score with time bonuses/penalties
7. Results displayed in modal
8. Assessment saved to database
9. Results visible on profile page

### Technical Flow
```
User Profile (skills, experience) 
    ↓
DeepSeek API Request
    ↓
Generated Questions (JSON)
    ↓
Display Questions with Timer
    ↓
User Submits Answers
    ↓
Score Calculation
    - Correctness: correct/total × 100
    - Time Factor: bonus/penalty based on speed
    - Wrong Penalty: -5 per wrong answer
    ↓
Save to Database (Assessment model)
    ↓
Display on Profile Page
```

## Files Modified/Created

### Models
- **users/models.py**: Added `Assessment` model

### Services
- **users/deepseek_service.py**: DeepSeek API integration class

### Views
- **PayoPrj/views.py**: 
  - `assessments()` - Main assessment view
  - `submit_assessment()` - Handle submission and scoring
- **users/views.py**: Updated `profile()` to show assessments

### Templates
- **users/templates/users/assessments.html**: Landing page
- **users/templates/users/assessment_test.html**: Test page with timer
- **users/templates/users/profile.html**: Shows assessment results

### URLs
- `/assessments/` - Assessment landing page
- `/assessments/?start=true` - Start new assessment
- `/assessments/submit/` - Submit assessment (POST)

## Database Schema

### Assessment Model
```python
class Assessment(models.Model):
    user = ForeignKey(User)
    skill_focus = CharField(max_length=255)
    total_questions = IntegerField(default=10)
    correct_answers = IntegerField(default=0)
    wrong_answers = IntegerField(default=0)
    total_time_seconds = IntegerField()
    score = DecimalField(max_digits=6, decimal_places=2)
    questions_data = JSONField()  # Stores questions, answers, user responses
    created_at = DateTimeField(auto_now_add=True)
```

## API Integration

### DeepSeek API
- **Endpoint**: https://api.deepseek.com/v1/chat/completions
- **API Key**: sk-8621b35578914df287cfc2206cca725b
- **Model**: deepseek-chat
- **Fallback**: 10 pre-defined questions if API fails

### Example API Request
```json
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "system",
      "content": "You are an expert technical interviewer..."
    },
    {
      "role": "user",
      "content": "Generate 10 MCQ questions for Python, Django..."
    }
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### Example API Response
```json
{
  "questions": [
    {
      "question": "What is Django ORM used for?",
      "options": {
        "A": "Database abstraction",
        "B": "Frontend rendering",
        "C": "API routing",
        "D": "Email sending"
      },
      "correct_answer": "A",
      "explanation": "ORM provides database abstraction layer"
    }
  ]
}
```

## Score Calculation Example

**Scenario**: User answers 8/10 correctly in 5 minutes (300 seconds)

1. **Base Score**: 8/10 × 100 = 80%
2. **Average Time**: 300/10 = 30 seconds per question
3. **Time Multiplier**: 1.0 (exactly 30s, no bonus/penalty)
4. **Wrong Answers**: 2 × 5 = 10 points penalty
5. **Final Score**: (80 × 1.0) - 10 = **70%**
6. **Grade**: B

## Profile Display

Assessment results appear on the user profile page below KYC verification status:

- Shows last 3 assessments
- Displays: Grade, Score %, Correct/Wrong/Total, Time taken
- "Take New Assessment" button
- If no assessments: Prompt to take first assessment

## Admin Panel

Assessments can be viewed in Django admin:
- Read-only (users can't manually create)
- Filter by date, score
- Search by username, skill focus
- Only superusers can delete

## Future Enhancements

1. Question difficulty progression (adaptive testing)
2. Detailed analytics dashboard
3. Skill-specific assessments
4. Certification upon passing threshold
5. Compare scores with similar users
6. Time limit per question
7. Question explanations after submission
8. Assessment categories (Python, JavaScript, etc.)

## Troubleshooting

### API Fails
- Fallback questions automatically used
- Check API key validity
- Verify internet connection

### Score Shows 0
- Check all questions were answered
- Verify time calculation
- Review scoring logic in submit_assessment()

### Questions Don't Match Skills
- Update user profile skills
- Check DeepSeek prompt template
- Verify skill extraction logic

## Security Considerations

1. CSRF protection on submission endpoint
2. Login required for all assessment views
3. User can only see their own assessments
4. API key stored securely (should move to environment variables)
5. JSON validation on question data
