"""
Test DeepSeek API integration for dynamic question generation
"""
from users.deepseek_service import DeepSeekQuestionGenerator

def test_api_generation():
    """Test question generation using DeepSeek API"""
    
    generator = DeepSeekQuestionGenerator()
    
    test_cases = [
        {
            "name": "Finance Professional",
            "skills": "Financial Analysis, Accounting, Budgeting",
            "experience": "5 years in corporate finance",
            "experience_level": "intermediate"
        },
        {
            "name": "Healthcare Nurse",
            "skills": "Patient Care, Nursing, Medical Records",
            "experience": "3 years nursing experience",
            "experience_level": "intermediate"
        },
        {
            "name": "Marketing Specialist",
            "skills": "Digital Marketing, SEO, Social Media",
            "experience": "4 years marketing experience",
            "experience_level": "intermediate"
        }
    ]
    
    print("=" * 80)
    print("TESTING DEEPSEEK API QUESTION GENERATION")
    print("=" * 80)
    
    for test_case in test_cases:
        print(f"\n{'=' * 80}")
        print(f"Test Case: {test_case['name']}")
        print(f"Skills: {test_case['skills']}")
        print(f"Experience Level: {test_case['experience_level']}")
        print("-" * 80)
        
        try:
            questions = generator.generate_questions(
                skills=test_case['skills'],
                experience=test_case['experience'],
                experience_level=test_case['experience_level'],
                num_questions=5  # Generate 5 questions for testing
            )
            
            print(f"\nGenerated {len(questions)} questions:\n")
            for i, q in enumerate(questions, 1):
                print(f"{i}. {q['question']}")
                print(f"   Options: {', '.join([f'{k}: {v[:30]}...' if len(v) > 30 else f'{k}: {v}' for k, v in q['options'].items()])}")
                print(f"   Correct: {q['correct_answer']}")
                print()
                
        except Exception as e:
            print(f"ERROR: {str(e)}")
        
        print()

if __name__ == "__main__":
    test_api_generation()
