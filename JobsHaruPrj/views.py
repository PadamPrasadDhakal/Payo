from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from organization.models import Job, Application
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

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

def assessments(request):
    # Example: pass an empty list or your actual assessments queryset
    assessments = []
    return render(request, "users/assessments.html", {"assessments": assessments}) 
def profile(request):
    # Example: pass an empty list or your actual assessments queryset
    profile = []
    return render(request, "users/profile.html", {"profile": profile})
def payment(request):
    payment = []
    return render(request, "users/payment.html", {"payment": payment})