"""
Custom decorators for protecting views based on user type
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import AccessMixin


def user_type_required(user_type):
    """
    Decorator to restrict access based on user type.
    
    Usage:
        @user_type_required('APP')  # For applicants only
        @user_type_required('ORG')  # For organizations only
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Check if user has the required user_type
            if hasattr(request.user, 'user_type') and request.user.user_type == user_type:
                return view_func(request, *args, **kwargs)
            else:
                # Redirect based on actual user type
                if request.user.user_type == 'ORG':
                    messages.warning(request, "⚠️ You don't have permission to access this page. This page is for applicants only.")
                    return redirect('/organization/profile/')
                else:
                    messages.warning(request, "⚠️ You don't have permission to access this page. This page is for organizations only.")
                    return redirect('/users/profile/')
        return wrapper
    return decorator


def applicant_required(view_func):
    """Decorator to restrict access to applicants only"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.user_type == 'APP':
            return view_func(request, *args, **kwargs)
        else:
            messages.warning(request, "⚠️ You don't have permission to access this page. This page is for applicants only.")
            return redirect('/organization/profile/')
    return wrapper


def organization_required(view_func):
    """Decorator to restrict access to organizations only"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.user_type == 'ORG':
            return view_func(request, *args, **kwargs)
        else:
            messages.warning(request, "⚠️ You don't have permission to access this page. This page is for organizations only.")
            return redirect('/users/profile/')
    return wrapper


# Class-based view mixins for protecting views based on user type
class ApplicantOnlyMixin(AccessMixin):
    """Mixin to restrict access to applicants only"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.user_type != 'APP':
            messages.warning(request, "⚠️ You don't have permission to access this page. This page is for applicants only.")
            return redirect('/organization/profile/')
        
        return super().dispatch(request, *args, **kwargs)


class OrganizationOnlyMixin(AccessMixin):
    """Mixin to restrict access to organizations only"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.user_type != 'ORG':
            messages.warning(request, "⚠️ You don't have permission to access this page. This page is for organizations only.")
            return redirect('/users/profile/')
        
        return super().dispatch(request, *args, **kwargs)
