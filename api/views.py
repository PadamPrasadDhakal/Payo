from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json

from users.models import User, SavedJob
from organization.models import Job, Application


@login_required
def user_tokens(request):
    user = request.user
    return JsonResponse({
        'tokens_left': user.tokens_left,
        'last_reset_at': user.last_token_reset.isoformat(),
        'tokens_restored': user.tokens_restored_flag
    })


@login_required
@csrf_exempt
def apply_job(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        
        if not job_id:
            return JsonResponse({'error': 'Job ID is required'}, status=400)
        
        with transaction.atomic():
            user = User.objects.select_for_update().get(id=request.user.id)
            
            if user.tokens_left <= 0:
                return JsonResponse({
                    'success': False,
                    'message': 'No tokens left for today',
                    'tokens_left': 0
                }, status=400)
            
            try:
                job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                return JsonResponse({'error': 'Job not found'}, status=404)
            
            # Check if already applied
            if Application.objects.filter(job=job, applicant=user).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Already applied to this job',
                    'tokens_left': user.tokens_left
                }, status=400)
            
            # Create application
            Application.objects.create(
                job=job,
                applicant=user,
                cover_letter="Applied via dashboard interface"
            )
            
            # Decrement tokens
            user.tokens_left -= 1
            user.save()
            
            return JsonResponse({
                'success': True,
                'tokens_left': user.tokens_left,
                'message': f'Application sent. {user.tokens_left} tokens left.'
            })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def job_list(request):
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    
    user = request.user
    applied_job_ids = Application.objects.filter(applicant=user).values_list('job_id', flat=True)
    
    jobs = Job.objects.exclude(id__in=applied_job_ids).exclude(posted_by=user).order_by('-created_at')
    
    paginator = Paginator(jobs, 10)
    page_obj = paginator.get_page(page)
    
    job_data = []
    for job in page_obj:
        job_data.append({
            'id': job.id,
            'title': job.title,
            'description': job.description[:200] + '...' if len(job.description) > 200 else job.description,
            'location': job.location or 'Remote',
            'salary': job.salary or 'Not specified',
            'job_type': job.get_job_type_display(),
            'posted_by': job.posted_by.organization_name or job.posted_by.username,
            'created_at': job.created_at.isoformat(),
        })
    
    return JsonResponse({
        'jobs': job_data,
        'hasNext': page_obj.has_next(),
        'hasPrevious': page_obj.has_previous(),
        'currentPage': page,
        'totalPages': paginator.num_pages,
        'count': paginator.count
    })


@login_required
def job_detail(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
        
        return JsonResponse({
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'requirements': job.requirements,
            'location': job.location or 'Remote',
            'salary': job.salary or 'Not specified',
            'job_type': job.get_job_type_display(),
            'posted_by': job.posted_by.organization_name or job.posted_by.username,
            'created_at': job.created_at.isoformat(),
            'deadline': job.deadline.isoformat() if job.deadline else None,
            'applications_count': job.applications.count()
        })
    
    except Job.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)


@login_required
@csrf_exempt
def saved_jobs(request):
    if request.method == 'GET':
        saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job').order_by('-saved_at')
        
        saved_jobs_data = []
        for saved_job in saved_jobs:
            job = saved_job.job
            saved_jobs_data.append({
                'id': saved_job.id,
                'job': {
                    'id': job.id,
                    'title': job.title,
                    'description': job.description[:200] + '...' if len(job.description) > 200 else job.description,
                    'location': job.location or 'Remote',
                    'salary': job.salary or 'Not specified',
                    'job_type': job.get_job_type_display(),
                    'posted_by': job.posted_by.organization_name or job.posted_by.username,
                },
                'saved_at': saved_job.saved_at.isoformat()
            })
        
        return JsonResponse({'saved_jobs': saved_jobs_data})
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            job_id = data.get('job_id')
            
            if not job_id:
                return JsonResponse({'error': 'Job ID is required'}, status=400)
            
            try:
                job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                return JsonResponse({'error': 'Job not found'}, status=404)
            
            saved_job, created = SavedJob.objects.get_or_create(
                user=request.user,
                job=job
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': 'Job saved successfully',
                    'saved_job_id': saved_job.id
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'Job already saved',
                    'saved_job_id': saved_job.id
                })
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@csrf_exempt
def delete_saved_job(request, saved_job_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        saved_job = SavedJob.objects.get(id=saved_job_id, user=request.user)
        saved_job.delete()
        return JsonResponse({'success': True, 'message': 'Job removed from saved list'})
    except SavedJob.DoesNotExist:
        return JsonResponse({'error': 'Saved job not found'}, status=404)


@login_required
@csrf_exempt
def ack_tokens_restored(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user = request.user
    user.tokens_restored_flag = False
    user.save()
    
    return JsonResponse({'success': True, 'message': 'Tokens restored flag cleared'})


@login_required
def application_detail(request, application_id):
    """Get detailed information about a specific application"""
    try:
        application = Application.objects.select_related('job', 'job__posted_by').get(
            id=application_id,
            applicant=request.user
        )
        
        job = application.job
        data = {
            'id': application.id,
            'status': application.get_status_display(),
            'status_code': application.status,
            'applied_date': application.created_at.isoformat(),
            'cover_letter': application.cover_letter,
            'notes': application.notes,
            'job': {
                'id': job.id,
                'title': job.title,
                'description': job.description,
                'requirements': job.requirements,
                'location': job.location or 'Remote',
                'salary': job.salary or 'Not specified',
                'job_type': job.get_job_type_display(),
                'posted_by': job.posted_by.organization_name or job.posted_by.username,
                'posted_date': job.created_at.isoformat(),
                'closing_date': job.get_closing_date().isoformat(),
                'is_expired': job.is_expired(),
                'days_remaining': job.days_remaining(),
            }
        }
        
        return JsonResponse({'success': True, 'application': data})
        
    except Application.DoesNotExist:
        return JsonResponse({'error': 'Application not found'}, status=404)


@login_required
@csrf_exempt
def withdraw_application(request, application_id):
    """Withdraw/cancel a job application"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        with transaction.atomic():
            application = Application.objects.select_for_update().get(
                id=application_id,
                applicant=request.user
            )
            
            # Check if application can be withdrawn
            if application.status in ['RJ', 'WD', 'HD']:
                status_display = {
                    'RJ': 'rejected',
                    'WD': 'already withdrawn',
                    'HD': 'hired'
                }
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot withdraw application that has been {status_display[application.status]}'
                }, status=400)
            
            # Mark as withdrawn
            application.status = 'WD'
            application.notes += f"\n[WITHDRAWN by user on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}]"
            application.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Application withdrawn successfully'
            })
            
    except Application.DoesNotExist:
        return JsonResponse({'error': 'Application not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def recent_application_updates(request):
    """Get recent status updates for user's applications"""
    try:
        # Get applications updated in the last 24 hours
        from datetime import timedelta
        recent_cutoff = timezone.now() - timedelta(days=1)
        
        updates = Application.objects.filter(
            applicant=request.user,
            reviewed_at__gte=recent_cutoff,
            reviewed_at__isnull=False
        ).select_related('job').order_by('-reviewed_at')[:10]
        
        update_list = []
        for app in updates:
            update_list.append({
                'id': app.id,
                'job_title': app.job.title,
                'status': app.status,
                'status_display': app.get_status_display(),
                'updated_at': app.reviewed_at.isoformat(),
                'notes': app.notes
            })
        
        return JsonResponse({
            'success': True,
            'updates': update_list
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)