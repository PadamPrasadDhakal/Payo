from django.http import JsonResponse
from django.shortcuts import redirect

class KycEnforcementMiddleware:
    """Prevent unverified organizations from creating/publishing jobs.

    - Blocks POST/PUT/PATCH requests to URLs containing '/organization/jobs' for org users
      whose KYC is not VERIFIED.
    - Allows read (GET) traffic.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            user = request.user
        except Exception:
            user = None

        # Only enforce for authenticated organization users on mutating requests
        if user and user.is_authenticated and getattr(user, 'user_type', None) == 'ORG':
            if request.method in ('POST', 'PUT', 'PATCH', 'DELETE') and '/organization/jobs' in request.path:
                # If user's KYC is not verified, block
                if not getattr(user, 'is_kyc_verified', False):
                    # If request is AJAX/JSON API, return 403 JSON
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                        return JsonResponse({'error': 'Organization KYC not verified. Cannot create or publish jobs.'}, status=403)
                    # Otherwise redirect to KYC page with message
                    return redirect('/kyc/')

        response = self.get_response(request)
        return response
