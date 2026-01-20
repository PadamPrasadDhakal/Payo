"""
Test script to demonstrate dynamic assessment question generation across various fields
"""
from users.deepseek_service import DeepSeekQuestionGenerator

def test_skill_matching():
    """Test question generation for different skill sets"""
    
    generator = DeepSeekQuestionGenerator()
    
    test_cases = [
        {
            "name": "Finance Professional",
            "skills": "Financial Analysis, Accounting, Budgeting",
            "experience_level": "intermediate"
        },
        {
            "name": "Healthcare Worker",
            "skills": "Patient Care, Nursing, Medical Records",
            "experience_level": "entry"
        },
        {
            "name": "Marketing Specialist",
            "skills": "Digital Marketing, SEO, Social Media, Content Creation",
            "experience_level": "intermediate"
        },
        {
            "name": "Customer Service Representative",
            "skills": "Customer Support, Communication, Problem Solving",
            "experience_level": "entry"
        },
        {
            "name": "HR Manager",
            "skills": "Recruitment, Employee Relations, Performance Management",
            "experience_level": "senior"
        },
        {
            "name": "Construction Worker",
            "skills": "Building, Safety, Blueprint Reading",
            "experience_level": "intermediate"
        },
        {
            "name": "Teacher",
            "skills": "Teaching, Classroom Management, Curriculum Development",
            "experience_level": "intermediate"
        },
        {
            "name": "Hospitality Staff",
            "skills": "Guest Service, Food and Beverage, Hotel Operations",
            "experience_level": "entry"
        },
        {
            "name": "Software Developer (for comparison)",
            "skills": "Python, JavaScript, Django, React",
            "experience_level": "intermediate"
        }
    ]
    
    print("=" * 80)
    print("DYNAMIC ASSESSMENT QUESTION GENERATION TEST")
    print("=" * 80)
    
    for test_case in test_cases:
        print(f"\n{'=' * 80}")
        print(f"Profile: {test_case['name']}")
        print(f"Skills: {test_case['skills']}")
        print(f"Experience Level: {test_case['experience_level']}")
        print("-" * 80)
        
        questions = generator.generate_questions(
            skills=test_case['skills'],
            experience="",
            experience_level=test_case['experience_level'],
            num_questions=5  # Generate 5 sample questions
        )
        
        print(f"\nGenerated {len(questions)} questions:\n")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q['question']}")
            print(f"   Correct Answer: {q['correct_answer']}")
        print()

if __name__ == "__main__":
    test_skill_matching()
