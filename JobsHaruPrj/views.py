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
    """
    Display available internships from the database.
    Internships are jobs where job_type = 'IN' (Internship).
    """
    from django.db.models import Q, Exists, OuterRef
    from organization.models import OrganizationFollow
    from django.core.paginator import Paginator
    
    # Get only internships (job_type = 'IN')
    internships_qs = Job.objects.filter(job_type='IN').select_related('posted_by').order_by('-created_at')
    
    # Check if user is authenticated and is an applicant for follow functionality
    followed_org_ids = []
    if request.user.is_authenticated and request.user.user_type == 'APP':
        # Annotate with whether they're from a followed organization
        internships_qs = internships_qs.annotate(
            is_followed_org=Exists(
                OrganizationFollow.objects.filter(
                    user=request.user,
                    organization=OuterRef('posted_by'),
                    is_active=True
                )
            )
        )
        # Order by: followed orgs first, then by creation date
        internships_qs = internships_qs.order_by('-is_followed_org', '-created_at')
        
        # Get followed org IDs for template
        followed_org_ids = list(OrganizationFollow.objects.filter(
            user=request.user,
            is_active=True
        ).values_list('organization_id', flat=True))
    
    # Apply search filter
    search_query = request.GET.get('search', '').strip()
    if search_query:
        internships_qs = internships_qs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(posted_by__organization_name__icontains=search_query)
        )
    
    # Apply location filter
    location_filter = request.GET.get('location', '').strip()
    if location_filter:
        internships_qs = internships_qs.filter(location__icontains=location_filter)
    
    # Pagination
    paginator = Paginator(internships_qs, 12)  # 12 internships per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check if user has already applied to any of these internships
    user_applied_internship_ids = []
    if request.user.is_authenticated and request.user.user_type == 'APP':
        user_applied_internship_ids = list(Application.objects.filter(
            applicant=request.user,
            job__job_type='IN'
        ).values_list('job_id', flat=True))
    
    context = {
        'internships': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'location_filter': location_filter,
        'followed_org_ids': followed_org_ids,
        'user_applied_internship_ids': user_applied_internship_ids,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, "users/internships.html", context) 

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


@login_required
def apply_internship(request, pk):
    """
    Handle internship application.
    - Reuses existing Application model with application_type='INT'
    - Does NOT affect user rankings/ratings
    - Prevents duplicate applications
    - Handles users without resumes gracefully
    """
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    
    # Get the internship (must be job_type='IN')
    internship = get_object_or_404(Job, pk=pk, job_type='IN')
    
    # Ensure user is an applicant
    if not request.user.is_applicant():
        messages.error(request, 'Only applicants can apply for internships.')
        return redirect('internships')
    
    # Check if internship is closed/expired
    if internship.is_expired():
        messages.error(request, 'This internship is no longer accepting applications.')
        return redirect('internships')
    
    # Check for duplicate application
    existing_application = Application.objects.filter(
        job=internship,
        applicant=request.user
    ).first()
    
    if existing_application:
        messages.warning(request, 'You have already applied for this internship.')
        return redirect('internships')
    
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '').strip()
        resume = request.FILES.get('resume')
        
        # If no resume uploaded, use user's existing resume
        if not resume and request.user.resume:
            resume_file = request.user.resume
        else:
            resume_file = resume
        
        # Create application (application_type is auto-set by save() method)
        application = Application(
            job=internship,
            applicant=request.user,
            cover_letter=cover_letter,
        )
        
        # Handle resume
        if resume:
            application.resume = resume
        elif request.user.resume:
            # Copy existing resume path
            application.resume = request.user.resume
        
        application.save()
        
        # Create notification for the organization
        from users.models import Notification
        Notification.objects.create(
            user=internship.posted_by,
            title='📩 New Internship Application',
            message=f'{request.user.get_full_name() or request.user.username} has applied for your internship: {internship.title}',
            notification_type='NEW_APPLICATION',
            related_id=application.id,
            action_url=f'/organization/applications/{internship.id}/'
        )
        
        # Create notification for the applicant
        Notification.objects.create(
            user=request.user,
            title='✅ Internship Application Submitted',
            message=f'Your application for {internship.title} at {internship.posted_by.organization_name or internship.posted_by.username} has been submitted successfully.',
            notification_type='APP_SUBMITTED',
            related_id=application.id,
            action_url='/users/applications/'
        )
        
        messages.success(request, 'Your internship application has been submitted successfully!')
        return redirect('internships')
    
    # GET request - show the application form
    context = {
        'internship': internship,
        'user_has_resume': bool(request.user.resume),
    }
    return render(request, 'users/apply_internship.html', context)