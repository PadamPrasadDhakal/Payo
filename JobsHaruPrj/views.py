from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from organization.models import Job, Application
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from users.models import Assessment
from users.deepseek_service import DeepSeekQuestionGenerator
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

def home_view(request):
    if request.user.is_authenticated:
        if request.user.is_organization():
            # Organizations go to their profile/dashboard
            return redirect('organization:profile')
        else:
            # Applicants go to their dashboard
            return render(request, "dashboard.html")
    return render(request, "home.html")

def contact_view(request):
    """Handle contact form submissions and send emails"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        query_type = request.POST.get('query_type', '').strip()
        custom_query = request.POST.get('custom_query', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validation
        if not all([name, email, phone, query_type, message]):
            return render(request, 'contact.html', {
                'error': 'Please fill in all required fields.',
                'success': False
            })
        
        # If custom query type is selected, use custom_query value
        if query_type == 'custom' and custom_query:
            query_type = custom_query
        elif query_type == 'custom':
            return render(request, 'contact.html', {
                'error': 'Please specify your custom query type.',
                'success': False
            })
        
        # Prepare email content
        subject = f'New Contact Query: {query_type}'
        email_message = f"""
New Contact Form Submission

Name: {name}
Email: {email}
Phone: {phone}
Query Type: {query_type}

Message:
{message}

---
This email was sent from the JobsHaru contact form.
        """
        
        try:
            # Send email to admin
            send_mail(
                subject=subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            
            # Optionally send confirmation email to user
            confirmation_subject = 'Thank you for contacting JobsHaru'
            confirmation_message = f"""
Dear {name},

Thank you for reaching out to us. We have received your query regarding "{query_type}" and our team will get back to you as soon as possible.

Your Query Details:
- Query Type: {query_type}
- Message: {message}

Best regards,
JobsHaru Team
            """
            
            send_mail(
                subject=confirmation_subject,
                message=confirmation_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,  # Don't fail if user email fails
            )
            
            return render(request, 'contact.html', {'success': True})
            
        except Exception as e:
            return render(request, 'contact.html', {
                'error': f'An error occurred while sending your query. Please try again later or contact us directly at {settings.CONTACT_EMAIL}.',
                'success': False
            })
    
    return render(request, 'contact.html', {'success': False})

def logout_view(request):
    logout(request)
    return redirect('home')
# def organizations(request):
#     return redirect('organizations')

def organizations(request):
    # Example: pass an empty list or your actual organizations queryset
    organizations = []
    return render(request, "users/organizations.html", {"organizations": organizations}) 

def internships(request):
    # Example: pass an empty list or your actual organizations queryset
    internships = []
    return render(request, "users/internships.html", {"internships": internships}) 

@login_required
def assessments(request):
    """Handle assessment start, display, and submission"""
    user = request.user
    
    # Get user's past assessments
    past_assessments = Assessment.objects.filter(user=user)[:5]
    
    # Check if user wants to start a new assessment
    if request.method == 'GET' and 'start' in request.GET:
        # Generate questions based on user profile
        generator = DeepSeekQuestionGenerator()
        
        skills = user.skills or "General IT, Programming"
        experience = user.experience or "Software development"
        experience_level = user.experience_level or "intermediate"
        
        # Generate 10 questions
        questions = generator.generate_questions(
            skills=skills,
            experience=experience,
            experience_level=experience_level,
            num_questions=10
        )
        
        # Store questions in session
        request.session['assessment_questions'] = questions
        request.session['assessment_start_time'] = timezone.now().isoformat()
        
        return render(request, 'users/assessment_test.html', {
            'questions': questions,
            'skill_focus': skills
        })
    
    return render(request, "users/assessments.html", {
        "past_assessments": past_assessments
    })

@login_required
@csrf_exempt
def submit_assessment(request):
    """Handle assessment submission and scoring"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body)
        user_answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)  # in seconds
        
        # Get questions from session
        questions = request.session.get('assessment_questions', [])
        
        if not questions:
            return JsonResponse({'error': 'No active assessment found'}, status=400)
        
        # Calculate scores
        correct_count = 0
        wrong_count = 0
        detailed_results = []
        
        for idx, question in enumerate(questions):
            q_id = f"q{idx}"
            user_answer = user_answers.get(q_id, '')
            correct_answer = question.get('correct_answer', '')
            
            is_correct = user_answer.upper() == correct_answer.upper()
            
            if is_correct:
                correct_count += 1
            else:
                wrong_count += 1
            
            detailed_results.append({
                'question': question.get('question'),
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question.get('explanation', '')
            })
        
        # Calculate final score with time bonus/penalty
        # Base score: correct answers / total questions * 100
        base_score = (correct_count / len(questions)) * 100
        
        # Time factor: 
        # - Fast completion (< 30 sec/question avg) gets bonus
        # - Slow completion (> 60 sec/question avg) gets penalty
        avg_time_per_question = time_taken / len(questions)
        
        time_multiplier = 1.0
        if avg_time_per_question < 30:
            time_multiplier = 1.1  # 10% bonus for quick answers
        elif avg_time_per_question > 60:
            time_multiplier = 0.9  # 10% penalty for slow answers
        
        # Wrong answer penalty: -5 points per wrong answer
        wrong_penalty = wrong_count * 5
        
        # Final score calculation
        final_score = max(0, (base_score * time_multiplier) - wrong_penalty)
        final_score = min(100, final_score)  # Cap at 100
        
        # Extract skills from user profile
        skill_focus = request.user.skills or "General Assessment"
        
        # Save assessment to database
        assessment = Assessment.objects.create(
            user=request.user,
            skill_focus=skill_focus[:255],
            total_questions=len(questions),
            correct_answers=correct_count,
            wrong_answers=wrong_count,
            total_time_seconds=int(time_taken),
            score=round(final_score, 2),
            questions_data={
                'questions': questions,
                'user_answers': user_answers,
                'detailed_results': detailed_results
            }
        )
        
        # Clear session data
        if 'assessment_questions' in request.session:
            del request.session['assessment_questions']
        if 'assessment_start_time' in request.session:
            del request.session['assessment_start_time']
        
        return JsonResponse({
            'success': True,
            'assessment_id': assessment.id,
            'score': float(final_score),
            'correct': correct_count,
            'wrong': wrong_count,
            'total': len(questions),
            'time_taken': time_taken,
            'grade': assessment.get_grade(),
            'redirect_url': f'/users/profile/'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 
def profile(request):
    # Example: pass an empty list or your actual assessments queryset
    profile = []
    return render(request, "users/profile.html", {"profile": profile})
def payment(request):
    payment = []
    return render(request, "users/payment.html", {"payment": payment})