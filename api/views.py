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
from users.models import IndividualKYC, OrganizationKYC, KycAudit
from users.forms_kyc import (
    IndividualKYCStep1Form, IndividualKYCStep2Form, IndividualKYCStep3Form,
    OrganizationKYCStep1Form, OrganizationKYCStep2Form, OrganizationKYCStep3Form
)
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.throttling import SimpleRateThrottle
from users.serializers import IndividualKYCSerializer, OrganizationKYCSerializer, KycAuditSerializer
from django.core.exceptions import PermissionDenied


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

            # Enforce KYC rate limit: unverified users can apply at most 2 jobs per calendar day
            if not user.is_kyc_verified:
                today = timezone.now().date()
                today_count = Application.objects.filter(applicant=user, created_at__date=today).count()
                if today_count >= 2:
                    return JsonResponse({'error': 'Unverified users can apply to 2 jobs per day. Complete KYC to remove this limit.'}, status=429)
            
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
@csrf_exempt
def kyc_list_create(request):
    """GET: list user's KYC records
       POST: create or update partial KYC for user (accepts 'type' and step/data)
    """
    try:
        if request.method == 'GET':
            user = request.user
            ind = None
            org = None
            try:
                ind = IndividualKYC.objects.get(user=user)
            except IndividualKYC.DoesNotExist:
                ind = None
            try:
                org = OrganizationKYC.objects.get(user=user)
            except OrganizationKYC.DoesNotExist:
                org = None

            data = {
                'individual': None,
                'organization': None
            }
            if ind:
                data['individual'] = {
                    'id': ind.id,
                    'status': ind.status,
                    'current_step': ind.current_step,
                    'submitted_at': ind.submitted_at.isoformat() if ind.submitted_at else None
                }
            if org:
                data['organization'] = {
                    'id': org.id,
                    'status': org.status,
                    'current_step': org.current_step,
                    'submitted_at': org.submitted_at.isoformat() if org.submitted_at else None
                }
            return JsonResponse({'success': True, 'kyc': data})

        elif request.method == 'POST':
            # Accept JSON or multipart form submissions. For files, frontend should send FormData.
            kyc_type = None
            step = 1
            data = {}
            files = {}
            # try JSON first
            try:
                payload = json.loads(request.body)
                kyc_type = payload.get('type')
                step = int(payload.get('step', 1))
                data = payload.get('data', {}) or {}
            except Exception:
                # fallback to form data
                kyc_type = request.POST.get('type')
                step = int(request.POST.get('step', 1) or 1)
                data = request.POST.dict()
                files = request.FILES

            if kyc_type == 'individual':
                obj, created = IndividualKYC.objects.get_or_create(user=request.user)
                # Validate using forms per step
                if step == 1:
                    form = IndividualKYCStep1Form(data or None, instance=obj)
                elif step == 2:
                    form = IndividualKYCStep2Form(data or None, files or None, instance=obj)
                else:
                    form = IndividualKYCStep3Form(data or None, instance=obj)

                if not form.is_valid():
                    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

                form.save()
                obj.current_step = step
                obj.save()
                return JsonResponse({'success': True, 'id': obj.id, 'status': obj.status})

            elif kyc_type == 'organization':
                obj, created = OrganizationKYC.objects.get_or_create(user=request.user)
                if step == 1:
                    form = OrganizationKYCStep1Form(data or None, instance=obj)
                elif step == 2:
                    form = OrganizationKYCStep2Form(data or None, files or None, instance=obj)
                else:
                    form = OrganizationKYCStep3Form(data or None, instance=obj)

                if not form.is_valid():
                    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

                form.save()
                obj.current_step = step
                obj.save()
                return JsonResponse({'success': True, 'id': obj.id, 'status': obj.status})

            else:
                return JsonResponse({'error': 'Invalid kyc type'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def kyc_detail(request, kyc_type, kyc_id):
    try:
        if kyc_type == 'individual':
            k = get_object_or_404(IndividualKYC, id=kyc_id, user=request.user)
        else:
            k = get_object_or_404(OrganizationKYC, id=kyc_id, user=request.user)

        # Return a simple representation
        resp = {}
        for field in ['id', 'status', 'current_step', 'submitted_at', 'updated_at']:
            val = getattr(k, field, None)
            resp[field] = val.isoformat() if hasattr(val, 'isoformat') else val

        return JsonResponse({'success': True, 'kyc': resp})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def kyc_submit(request, kyc_type, kyc_id):
    """User submits KYC for review (sets status to SUBMITTED)"""
    if request.method != 'PATCH':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        if kyc_type == 'individual':
            k = get_object_or_404(IndividualKYC, id=kyc_id, user=request.user)
        else:
            k = get_object_or_404(OrganizationKYC, id=kyc_id, user=request.user)

        k.status = 'SUBMITTED'
        k.submitted_at = timezone.now()
        k.save()
        KycAudit.objects.create(kyc_type='IND' if kyc_type=='individual' else 'ORG', kyc_id=k.id, actor=request.user, action='SUBMITTED', message='User submitted KYC')
        return JsonResponse({'success': True, 'message': 'KYC submitted for review', 'status': k.status})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def kyc_admin_action(request, kyc_type, kyc_id):
    """Admin endpoint to verify/reject/request_more_info for a KYC record"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin privileges required'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        payload = json.loads(request.body)
        action = payload.get('status')  # VERIFIED|REJECTED|REQUEST_MORE_INFO
        reason = payload.get('reason', '')
        missing_fields = payload.get('missing_fields', [])

        if kyc_type == 'individual':
            k = get_object_or_404(IndividualKYC, id=kyc_id)
            k.user_ref = k.user
        else:
            k = get_object_or_404(OrganizationKYC, id=kyc_id)
            k.user_ref = k.user

        if action == 'VERIFIED':
            k.status = 'VERIFIED'
            k.save()
            k.user.is_kyc_verified = True
            k.user.save(update_fields=['is_kyc_verified'])
            KycAudit.objects.create(kyc_type='IND' if kyc_type=='individual' else 'ORG', kyc_id=k.id, actor=request.user, action='VERIFIED', message=reason)
            return JsonResponse({'success': True, 'status': 'VERIFIED'})
        elif action == 'REJECTED':
            k.status = 'REJECTED'
            k.save()
            k.user.is_kyc_verified = False
            k.user.save(update_fields=['is_kyc_verified'])
            KycAudit.objects.create(kyc_type='IND' if kyc_type=='individual' else 'ORG', kyc_id=k.id, actor=request.user, action='REJECTED', message=reason)
            return JsonResponse({'success': True, 'status': 'REJECTED'})
        elif action == 'REQUEST_MORE_INFO':
            k.status = 'DRAFT'
            k.save()
            KycAudit.objects.create(kyc_type='IND' if kyc_type=='individual' else 'ORG', kyc_id=k.id, actor=request.user, action='REQUEST_MORE_INFO', message=json.dumps({'missing_fields': missing_fields, 'note': reason}))
            return JsonResponse({'success': True, 'status': 'DRAFT'})
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
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
        # Get applications updated in the last 48 hours (extended window)
        from datetime import timedelta
        recent_cutoff = timezone.now() - timedelta(hours=48)
        
        # Get recent updates
        updates = Application.objects.filter(
            applicant=request.user,
            reviewed_at__gte=recent_cutoff,
            reviewed_at__isnull=False
        ).select_related('job').order_by('-reviewed_at')[:15]
        
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
            'updates': update_list,
            'count': len(update_list),
            'cutoff_time': recent_cutoff.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class UnverifiedUserRateThrottle(SimpleRateThrottle):
    """Throttle that limits unverified users to 2 applications per day.

    Returns None (no throttling) for verified users.
    """
    scope = 'unverified_apply'

    def get_cache_key(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return None
        # Only throttle unverified users
        if getattr(user, 'is_kyc_verified', False):
            return None

        # Use user id + date as key
        ident = f"unverified_apply_{user.id}_{timezone.now().date().isoformat()}"
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class ApplyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UnverifiedUserRateThrottle]

    def post(self, request, *args, **kwargs):
        job_id = request.data.get('job_id') or request.data.get('id')
        if not job_id:
            return Response({'error': 'Job ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.select_for_update().get(id=request.user.id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

        if Application.objects.filter(job=job, applicant=user).exists():
            return Response({'success': False, 'message': 'Already applied to this job'}, status=status.HTTP_400_BAD_REQUEST)

        # Additional server-side KYC limit: unverified users limited to 2 apps/day
        if not user.is_kyc_verified:
            today = timezone.now().date()
            today_count = Application.objects.filter(applicant=user, created_at__date=today).count()
            if today_count >= 2:
                return Response({'error': 'Unverified users can apply to 2 jobs per day. Complete KYC to remove this limit.'}, status=429)

        # Create application
        Application.objects.create(job=job, applicant=user, cover_letter=request.data.get('cover_letter', 'Applied via API'))

        # Optional tokens decrement (if implemented)
        if hasattr(user, 'tokens_left') and user.tokens_left > 0:
            user.tokens_left -= 1
            user.save(update_fields=['tokens_left'])

        return Response({'success': True, 'message': 'Application sent.'})


class KYCListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        ind = None
        org = None
        try:
            ind = IndividualKYC.objects.get(user=user)
        except IndividualKYC.DoesNotExist:
            ind = None
        try:
            org = OrganizationKYC.objects.get(user=user)
        except OrganizationKYC.DoesNotExist:
            org = None

        data = {
            'individual': IndividualKYCSerializer(ind).data if ind else None,
            'organization': OrganizationKYCSerializer(org).data if org else None
        }
        return Response({'success': True, 'kyc': data})

    def post(self, request):
        # Accept JSON or multipart/form-data. Use forms for validation per step.
        kyc_type = request.data.get('type') or request.POST.get('type')
        step = int(request.data.get('step', request.POST.get('step', 1)))
        payload = request.data.get('data') or request.data or request.POST.dict()

        if kyc_type == 'individual':
            obj, created = IndividualKYC.objects.get_or_create(user=request.user)
            if step == 1:
                form = IndividualKYCStep1Form(payload, instance=obj)
            elif step == 2:
                form = IndividualKYCStep2Form(payload, request.FILES or None, instance=obj)
            else:
                form = IndividualKYCStep3Form(payload, instance=obj)

            if not form.is_valid():
                return Response({'success': False, 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

            form.save()
            obj.current_step = step
            obj.save()
            return Response({'success': True, 'id': obj.id, 'status': obj.status})

        elif kyc_type == 'organization':
            obj, created = OrganizationKYC.objects.get_or_create(user=request.user)
            if step == 1:
                form = OrganizationKYCStep1Form(payload, instance=obj)
            elif step == 2:
                form = OrganizationKYCStep2Form(payload, request.FILES or None, instance=obj)
            else:
                form = OrganizationKYCStep3Form(payload, instance=obj)

            if not form.is_valid():
                return Response({'success': False, 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

            form.save()
            obj.current_step = step
            obj.save()
            return Response({'success': True, 'id': obj.id, 'status': obj.status})

        return Response({'error': 'Invalid kyc type'}, status=status.HTTP_400_BAD_REQUEST)


class KYCDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, kyc_type, kyc_id):
        if kyc_type == 'individual':
            k = get_object_or_404(IndividualKYC, id=kyc_id, user=request.user)
            return Response(IndividualKYCSerializer(k).data)
        else:
            k = get_object_or_404(OrganizationKYC, id=kyc_id, user=request.user)
            return Response(OrganizationKYCSerializer(k).data)


class KYCSubmitAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, kyc_type, kyc_id):
        if kyc_type == 'individual':
            k = get_object_or_404(IndividualKYC, id=kyc_id, user=request.user)
        else:
            k = get_object_or_404(OrganizationKYC, id=kyc_id, user=request.user)

        k.status = 'SUBMITTED'
        k.submitted_at = timezone.now()
        k.save()
        KycAudit.objects.create(kyc_type='IND' if kyc_type=='individual' else 'ORG', kyc_id=k.id, actor=request.user, action='SUBMITTED', message='User submitted KYC')
        return Response({'success': True, 'status': k.status})


class KYCAdminActionAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, kyc_type, kyc_id):
        action = request.data.get('status')
        reason = request.data.get('reason', '')
        missing_fields = request.data.get('missing_fields', [])

        if kyc_type == 'individual':
            k = get_object_or_404(IndividualKYC, id=kyc_id)
        else:
            k = get_object_or_404(OrganizationKYC, id=kyc_id)

        if action == 'VERIFIED':
            k.status = 'VERIFIED'
            k.save()
            k.user.is_kyc_verified = True
            k.user.save(update_fields=['is_kyc_verified'])
            KycAudit.objects.create(kyc_type='IND' if kyc_type=='individual' else 'ORG', kyc_id=k.id, actor=request.user, action='VERIFIED', message=reason)
            return Response({'success': True, 'status': 'VERIFIED'})
        elif action == 'REJECTED':
            k.status = 'REJECTED'
            k.save()
            k.user.is_kyc_verified = False
            k.user.save(update_fields=['is_kyc_verified'])
            KycAudit.objects.create(kyc_type='IND' if kyc_type=='individual' else 'ORG', kyc_id=k.id, actor=request.user, action='REJECTED', message=reason)
            return Response({'success': True, 'status': 'REJECTED'})
        elif action == 'REQUEST_MORE_INFO':
            k.status = 'DRAFT'
            k.save()
            KycAudit.objects.create(kyc_type='IND' if kyc_type=='individual' else 'ORG', kyc_id=k.id, actor=request.user, action='REQUEST_MORE_INFO', message=json.dumps({'missing_fields': missing_fields, 'note': reason}))
            return Response({'success': True, 'status': 'DRAFT'})
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)