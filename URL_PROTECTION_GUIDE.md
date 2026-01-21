# URL Protection Mechanism - Payo

## Overview
This document explains the URL protection mechanism implemented to prevent unauthorized access. Users logged in as **Applicants** cannot access **Organization URLs** and vice versa.

## Architecture

### 1. Custom Decorators (`users/decorators.py`)

#### Function-Based View Decorators:
- **`@applicant_required`** - Only applicants can access
- **`@organization_required`** - Only organizations can access
- **`@user_type_required(user_type)`** - Generic decorator for specific user types

#### Class-Based View Mixins:
- **`ApplicantOnlyMixin`** - For class-based views requiring applicant access
- **`OrganizationOnlyMixin`** - For class-based views requiring organization access

### 2. How It Works

#### User Type Check:
```python
# User model has user_type field with choices:
# 'APP' = Applicant
# 'ORG' = Organization

if request.user.user_type == 'APP':
    # Applicant access
elif request.user.user_type == 'ORG':
    # Organization access
```

#### When Access is Denied:
1. User is shown a warning message: "⚠️ You don't have permission to access this page. This page is [for applicants/for organizations] only."
2. User is redirected to their appropriate dashboard:
   - **Applicants** → `/users/profile/`
   - **Organizations** → `/organization/profile/`

---

## Protected URLs

### Organization-Only URLs (Protected with `@organization_required`)

| URL | View | Purpose |
|-----|------|---------|
| `/organization/` | organization_list_view | List organization jobs |
| `/organization/dashboard/` | org_dashboard | Organization dashboard |
| `/organization/profile/` | org_profile | View organization profile |
| `/organization/profile/edit/` | org_profile_edit | Edit organization profile |
| `/organization/jobs/` | org_jobs | View all posted jobs |
| `/organization/jobs/new/` | JobCreateView/OrgJobCreateView | Create new job posting |
| `/organization/applications/` | applications_overview | View all applications |
| `/organization/applications/<id>/` | application_detail | View specific application details |
| `/organization/payment/` | payment_page | Payment page for plans |
| `/organization/payment/process/` | process_payment | Process payment |

### Applicant-Only URLs (Protected with `@applicant_required`)

| URL | View | Purpose |
|-----|------|---------|
| `/users/profile/edit/` | profile_edit | Edit applicant profile |
| `/users/add-info/` | add_info | Complete Google OAuth profile |
| `/users/dash-jobs/` | dash_jobs | View job listings dashboard |
| `/users/applications/` | applications_dashboard | View own job applications |
| `/jobs/<id>/apply/` | apply_job | Apply to a job |

### Shared URLs (Accessible by Both)

| URL | View | Purpose |
|-----|------|---------|
| `/users/change-password/` | change_password | Change password (both user types) |
| `/users/kyc/` | kyc_form_view | KYC verification (both user types) |
| `/users/profile/` | profile | View own profile (both user types) |

---

## Implementation Examples

### Function-Based View Example:
```python
from users.decorators import applicant_required

@applicant_required
def profile_edit(request):
    # Only applicants can access this view
    user = request.user
    # ... rest of the view logic
```

### Class-Based View Example:
```python
from users.decorators import OrganizationOnlyMixin
from django.views.generic import ListView

class JobListView(OrganizationOnlyMixin, ListView):
    model = Job
    template_name = "organization/job_list.html"
    # ... rest of the class
```

### Inline Check Example:
```python
@login_required
def payment_page(request):
    """Payment page for organizations"""
    if request.user.user_type != 'ORG':
        messages.warning(request, "⚠️ This page is for organizations only.")
        return redirect('/users/profile/')
    # ... rest of the view logic
```

---

## Class-Based View Protection

For **ListView** and **DetailView** classes, protection is added via dispatch method:

```python
class JobListView(LoginRequiredMixin, ListView):
    model = Job
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'ORG':
            messages.warning(request, "⚠️ You don't have permission to access this page.")
            return redirect('/users/profile/')
        return super().dispatch(request, *args, **kwargs)
```

---

## User Experience Flow

### Scenario 1: Applicant tries to access organization URL
```
1. Applicant logged in as user_type='APP'
2. Tries to access /organization/dashboard/
3. @organization_required decorator checks user type
4. Access denied, warning message shown
5. User redirected to /users/profile/
```

### Scenario 2: Organization tries to access applicant URL
```
1. Organization logged in as user_type='ORG'
2. Tries to access /users/applications/
3. @applicant_required decorator checks user type
4. Access denied, warning message shown
5. User redirected to /organization/profile/
```

### Scenario 3: User accesses shared URLs
```
1. Either user type tries to access /users/change-password/
2. @login_required decorator verifies authentication (no type check)
3. Access granted
4. Both applicants and organizations can change passwords
```

---

## Message Display

When a user tries to access a protected URL:

**For Applicants trying organization URLs:**
```
⚠️ You don't have permission to access this page. 
This page is for organizations only.
```

**For Organizations trying applicant URLs:**
```
⚠️ You don't have permission to access this page. 
This page is for applicants only.
```

Messages are displayed using Django's messaging framework and appear in the UI via alert boxes.

---

## Files Modified

1. **`users/decorators.py`** (NEW)
   - Created custom decorators and mixins for URL protection

2. **`users/views.py`**
   - Added decorator imports
   - Applied `@applicant_required` to:
     - `profile_edit()`
     - `add_info()`
     - `dash_jobs()`
     - `applications_dashboard()`

3. **`organization/views.py`**
   - Added decorator imports
   - Applied `@organization_required` to:
     - `organization_list_view()`
     - `org_dashboard()`
     - `org_profile()`
     - `org_jobs()`
     - `org_profile_edit()`
     - `applications_overview()`
     - `application_detail()`
     - `payment_page()`
     - `process_payment()`
   - Added dispatch checks to class-based views:
     - `JobListView`
     - `JobDetailView`
     - `JobCreateView`
     - `OrgJobCreateView`
   - Applied `@applicant_required` to:
     - `apply_job()`

---

## Testing the Protection

### Test Case 1: Applicant Cannot Access Organization URLs
```
1. Login as an applicant
2. Try to access /organization/dashboard/
3. Expected: Redirected to /users/profile/ with warning message
```

### Test Case 2: Organization Cannot Access Applicant URLs
```
1. Login as an organization
2. Try to access /users/applications/
3. Expected: Redirected to /organization/profile/ with warning message
```

### Test Case 3: Proper Access Allowed
```
1. Login as applicant
2. Access /users/profile/ or /users/applications/
3. Expected: Full access granted
```

---

## Security Benefits

1. ✅ **Prevents Unauthorized Access** - Users can't browse other user type URLs
2. ✅ **Role-Based Access Control** - Different dashboards for applicants and organizations
3. ✅ **Clear User Feedback** - Warning messages explain why access was denied
4. ✅ **Consistent Protection** - All user-type-specific views are protected
5. ✅ **DRY (Don't Repeat Yourself)** - Reusable decorators instead of repeating logic
6. ✅ **Maintainable** - Easy to add protection to new views

---

## Future Enhancements

1. Add granular permissions (e.g., can_post_jobs, can_view_applications)
2. Implement permission levels within user types
3. Add audit logging for access attempts
4. Create custom error pages for access denied
5. Add optional 2FA for sensitive operations

---

## Support

For issues or questions about URL protection:
1. Check if the decorator is imported correctly
2. Verify user_type field is set correctly in the database
3. Check browser console for any JavaScript errors
4. Review Django debug toolbar for view execution flow
