from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import User
from organization.models import Job


@login_required
def debug_tokens(request):
    """Debug view to check token system"""
    user = request.user
    
    # Get user info
    user_data = {
        'username': user.username,
        'user_type': user.get_user_type_display(),
        'tokens_left': user.tokens_left,
        'last_token_reset': user.last_token_reset.isoformat() if user.last_token_reset else None,
        'tokens_restored_flag': user.tokens_restored_flag,
    }
    
    # Get some stats
    total_users = User.objects.count()
    total_jobs = Job.objects.count()
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'user': user_data,
            'stats': {
                'total_users': total_users,
                'total_jobs': total_jobs,
            }
        })
    
    return render(request, 'debug_tokens.html', {
        'user_data': user_data,
        'total_users': total_users,
        'total_jobs': total_jobs,
    })