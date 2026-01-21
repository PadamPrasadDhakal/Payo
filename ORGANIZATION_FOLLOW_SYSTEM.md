# Organization Follow System Documentation

## Overview
This document describes the comprehensive Organization Follow System implemented for Payo - a feature that allows job seekers (applicants) to follow organizations and receive prioritized job listings from those organizations.

## Table of Contents
1. [Features](#features)
2. [Database Schema](#database-schema)
3. [URL Routes](#url-routes)
4. [Views & Logic](#views--logic)
5. [Templates](#templates)
6. [JavaScript Functions](#javascript-functions)
7. [Permissions & Access Control](#permissions--access-control)
8. [Testing Guide](#testing-guide)
9. [Future Enhancements](#future-enhancements)

---

## Features

### ✅ Implemented Features

1. **Organizations Directory**
   - Public page displaying all registered organizations
   - Accessible to logged-in and logged-out users (applicants only)
   - Organizations are redirected with error message
   - Shows: organization logo, name, industry, location, follower count, job count
   - Pagination (20 organizations per page)
   - Search by organization name or industry
   - Filter by industry and location

2. **Follow/Unfollow System**
   - Only applicants can follow organizations
   - AJAX-based (no page reload)
   - Follow button changes to "Following" with checkmark
   - Hover over "Following" shows unfollow state (turns red)
   - Real-time follower count updates
   - Deactivation model (maintains follow history)
   - Unique constraint prevents duplicate follows
   - Toast notifications for success/error

3. **Login Prompt for Logged-Out Users**
   - Modal popup when logged-out user clicks "Follow"
   - Redirects to login page with next parameter
   - Returns user to same page after login

4. **Job Listing Prioritization**
   - Logged-in applicants see followed organizations' jobs first
   - Jobs sorted by: is_followed_org DESC, created_at DESC
   - Section header: "Jobs from Organizations You Follow"
   - Maintains existing search and filter functionality
   - Works for logged-out users (shows normal listing)

5. **Follow Indicators on Job Cards**
   - Each job card shows organization info
   - Follow/Following button on job cards
   - Clicking follow button doesn't redirect (AJAX)
   - Button state updates across all instances on page
   - Shows organization logo, name, industry

6. **Permissions & Access Control**
   - Organizations cannot access organizations directory
   - Only applicants can follow/unfollow
   - Proper HTTP status codes (401, 403, 404, 400)
   - CSRF protection on all POST requests

7. **Database Optimization**
   - select_related() for foreign keys
   - prefetch_related() for many-to-many
   - Annotate with follower count using Count()
   - Annotate with is_followed using Exists()
   - Database indexes on user and organization fields

---

## Database Schema

### OrganizationFollow Model

```python
class OrganizationFollow(models.Model):
    user = ForeignKey(User, related_name="following_organizations")
        # Limit to applicants only
    
    organization = ForeignKey(User, related_name="followers")
        # Limit to organizations only
    
    followed_at = DateTimeField(auto_now_add=True)
    is_active = BooleanField(default=True)
    
    class Meta:
        unique_together = ('user', 'organization')
        ordering = ['-followed_at']
        indexes = [
            Index(fields=['user', 'is_active']),
            Index(fields=['organization', 'is_active']),
        ]
```

**Relationships:**
- `User.following_organizations` - All organizations this user follows
- `User.followers` - All users following this organization

**Indexes:**
- Composite index on (user, is_active)
- Composite index on (organization, is_active)
- Improves query performance for checking follow status

---

## URL Routes

All routes are under the `organization` app namespace:

```python
# Organizations Directory
path('organizations/directory/', organizations_directory, 
     name='organizations-directory')

# Follow/Unfollow API Endpoints
path('organizations/follow/<int:org_id>/', follow_organization, 
     name='follow-organization')
path('organizations/unfollow/<int:org_id>/', unfollow_organization, 
     name='unfollow-organization')
```

**Full URLs:**
- `/organizations/directory/` - Browse all organizations
- `/organizations/follow/123/` - Follow organization with ID 123 (POST)
- `/organizations/unfollow/123/` - Unfollow organization with ID 123 (POST)

---

## Views & Logic

### 1. organizations_directory(request)

**Purpose:** Display all organizations with search/filter capabilities

**Logic:**
```python
1. Check if user is organization → redirect with error
2. Get all organizations (user_type='ORG')
3. Annotate with follower_count
4. If user is logged-in applicant:
   - Annotate with is_followed status
5. Apply search filter (name, username, industry)
6. Apply industry filter
7. Apply location filter
8. Order by: follower_count DESC, organization_name ASC
9. Paginate (20 per page)
10. Render template with context
```

**Query Optimization:**
- Uses `Count()` for follower count (single query)
- Uses `Exists()` for is_followed check (single query)
- No N+1 problem

**Context Variables:**
- `page_obj` - Paginated organizations
- `organizations` - Current page organizations
- `search_query` - Current search term
- `industry_filter` - Selected industry
- `location_filter` - Selected location
- `all_industries` - Available industries for dropdown
- `all_locations` - Available locations for dropdown
- `total_count` - Total organizations count

---

### 2. follow_organization(request, org_id)

**Purpose:** Create follow relationship (AJAX endpoint)

**Decorators:** `@login_required`, `@require_POST`

**Logic:**
```python
1. Check user is applicant → 403 error if not
2. Get organization by org_id → 404 if not found
3. Check if follow already exists:
   a. If exists and active → 400 error (already following)
   b. If exists but inactive → reactivate it
   c. If doesn't exist → create new follow
4. Get updated follower count
5. Return JSON response with success/follower_count
```

**Response Format:**
```json
{
    "success": true,
    "message": "You are now following Acme Corp",
    "follower_count": 42,
    "is_following": true
}
```

**Error Responses:**
- 403: User is not an applicant
- 404: Organization not found
- 400: Already following this organization

---

### 3. unfollow_organization(request, org_id)

**Purpose:** Deactivate follow relationship (AJAX endpoint)

**Decorators:** `@login_required`, `@require_POST`

**Logic:**
```python
1. Check user is applicant → 403 error if not
2. Get organization by org_id → 404 if not found
3. Get active follow relationship → 400 if not exists
4. Deactivate follow (is_active = False)
5. Get updated follower count
6. Return JSON response with success/follower_count
```

**Response Format:**
```json
{
    "success": true,
    "message": "You have unfollowed Acme Corp",
    "follower_count": 41,
    "is_following": false
}
```

**Note:** Deactivates instead of deleting to maintain follow history

---

### 4. JobListView (Modified)

**Purpose:** Display jobs with prioritization for followed organizations

**Key Changes:**
```python
def get_queryset(self):
    queryset = Job.objects.select_related('posted_by').all()
    
    # If user is logged-in applicant
    if user.is_authenticated and user.user_type == 'APP':
        # Annotate with is_followed_org
        queryset = queryset.annotate(
            is_followed_org=Exists(
                OrganizationFollow.objects.filter(
                    user=request.user,
                    organization=OuterRef('posted_by'),
                    is_active=True
                )
            )
        )
        # Order: followed orgs first, then by date
        queryset = queryset.order_by('-is_followed_org', '-created_at')
    else:
        # Normal ordering for non-applicants
        queryset = queryset.order_by('-created_at')
    
    # Apply filters (search, location, job_type)
    # ...
    
    return queryset

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Add followed_org_ids for JavaScript
    if user.is_authenticated and user.user_type == 'APP':
        followed_org_ids = OrganizationFollow.objects.filter(
            user=request.user,
            is_active=True
        ).values_list('organization_id', flat=True)
        context['followed_org_ids'] = list(followed_org_ids)
    
    return context
```

**Result:**
- Jobs from followed organizations appear first
- Within each group, sorted by newest first
- Maintains search/filter functionality

---

## Templates

### 1. organizations_directory.html

**Location:** `templates/organization/organizations_directory.html`

**Key Components:**
- Header with title and total count
- Search and filter form (search, industry, location)
- Organization cards grid (3 columns on desktop)
- Each card shows:
  - Logo or placeholder
  - Organization name
  - Industry and location badges
  - Description (truncated)
  - Follower count and job count
  - Follow/Following button
  - "View Profile" link
- Pagination controls
- Login required modal
- JavaScript for follow/unfollow

**Responsive Design:**
- Desktop: 3 columns
- Tablet: 2 columns
- Mobile: 1 column

---

### 2. jobs/job_list.html (Modified)

**Location:** `jobs/templates/jobs/job_list.html`

**Key Additions:**
- Search and filter form
- Section header for followed organizations
- Organization info section on each job card:
  - Logo
  - Name
  - Industry
  - Follow button
- Follow buttons update across all instances
- Link to organizations directory
- JavaScript for follow/unfollow from job cards

---

## JavaScript Functions

### Core Functions

```javascript
// Get CSRF token
function getCookie(name) { /* ... */ }

// Follow organization
function followOrganization(orgId) {
    // Update button to loading state
    // POST to /organizations/follow/{orgId}/
    // On success:
    //   - Update button to "Following"
    //   - Update follower count
    //   - Show success toast
    // On error:
    //   - Revert button state
    //   - Show error toast
}

// Unfollow organization
function unfollowOrganization(orgId) {
    // Update button to loading state
    // POST to /organizations/unfollow/{orgId}/
    // On success:
    //   - Update button to "Follow"
    //   - Update follower count
    //   - Show success toast
    // On error:
    //   - Revert button state
    //   - Show error toast
}

// Follow from job card (same as above but updates all buttons)
function followOrganizationFromJob(orgId) { /* ... */ }

// Unfollow from job card
function unfollowOrganizationFromJob(orgId) { /* ... */ }

// Handle login required
function handleLoginRequired() {
    // Show modal or redirect to login
}

// Show toast notification
function showToast(type, message) {
    // Create and display toast notification
    // Auto-remove after 5 seconds
}
```

### Button States

1. **Initial State (Not Following):**
   ```html
   <button class="btn-follow" onclick="followOrganization(123)">
       <i class="fas fa-plus"></i> Follow
   </button>
   ```

2. **Loading State:**
   ```html
   <button class="btn-loading" disabled>
       <i class="fas fa-spinner fa-spin"></i> Following...
   </button>
   ```

3. **Following State:**
   ```html
   <button class="btn-following" onclick="unfollowOrganization(123)">
       <i class="fas fa-check"></i> Following
   </button>
   ```

4. **Hover over Following:**
   - Button turns red
   - Icon changes to X
   - Text changes to "Unfollow"

---

## Permissions & Access Control

### Access Matrix

| Feature | Logged-Out User | Applicant | Organization |
|---------|----------------|-----------|--------------|
| View Organizations Directory | ✅ Yes | ✅ Yes | ❌ Redirect |
| Follow Organization | ❌ Login Required | ✅ Yes | ❌ 403 Error |
| Unfollow Organization | ❌ Login Required | ✅ Yes | ❌ 403 Error |
| See Prioritized Jobs | ❌ No | ✅ Yes | ❌ N/A |
| View Job Listings | ✅ Yes | ✅ Yes | ✅ Yes |

### HTTP Status Codes

- **200 OK:** Successful GET requests
- **400 Bad Request:** Invalid request (e.g., already following)
- **401 Unauthorized:** Not authenticated (for protected endpoints)
- **403 Forbidden:** Wrong user type (organization trying applicant feature)
- **404 Not Found:** Organization doesn't exist

### Security Measures

1. **CSRF Protection:** All POST requests require CSRF token
2. **User Type Validation:** Checked on both frontend and backend
3. **Database Constraints:** unique_together prevents duplicate follows
4. **Model Validation:** clean() method validates user types
5. **Decorator Protection:** @login_required, @require_POST

---

## Testing Guide

### Manual Testing Checklist

#### 1. Organizations Directory
- [ ] Logged-out user can access directory
- [ ] Logged-in applicant can access directory
- [ ] Organization trying to access gets redirected
- [ ] Search by organization name works
- [ ] Filter by industry works
- [ ] Filter by location works
- [ ] Pagination works correctly
- [ ] Follower count displays correctly
- [ ] Job count displays correctly

#### 2. Follow Functionality
- [ ] Logged-out user clicking Follow shows login prompt
- [ ] Applicant can follow an organization
- [ ] "Follow" button changes to "Following" after click
- [ ] Follower count increments by 1
- [ ] No page reload occurs (AJAX)
- [ ] Success toast notification appears
- [ ] Following same organization twice shows error

#### 3. Unfollow Functionality
- [ ] Applicant can unfollow an organization
- [ ] "Following" button changes to "Follow" after click
- [ ] Follower count decrements by 1
- [ ] No page reload occurs (AJAX)
- [ ] Success toast notification appears
- [ ] Unfollowing non-followed org shows error

#### 4. Job Listing Prioritization
- [ ] Followed organization jobs appear first
- [ ] Jobs are sorted correctly within groups
- [ ] Section header shows for followed jobs
- [ ] Search still works with prioritization
- [ ] Filters still work with prioritization
- [ ] Logged-out users see normal listing

#### 5. Job Card Follow Buttons
- [ ] Follow button shows on each job card
- [ ] Clicking follow button on job card works
- [ ] All instances of same org update together
- [ ] No redirect occurs (stays on job list)
- [ ] Toast notification appears
- [ ] Button states persist after page reload

#### 6. Permissions
- [ ] Organization cannot follow organizations
- [ ] Organization gets 403 error on follow attempt
- [ ] Applicant can only follow organizations (not other applicants)
- [ ] CSRF token required for POST requests

### Automated Testing (Recommended)

```python
# tests/test_organization_follow.py

from django.test import TestCase, Client
from users.models import User
from organization.models import OrganizationFollow

class OrganizationFollowTestCase(TestCase):
    def setUp(self):
        # Create applicant user
        self.applicant = User.objects.create_user(
            username='applicant1',
            email='applicant@test.com',
            password='pass123',
            user_type='APP'
        )
        
        # Create organization user
        self.org = User.objects.create_user(
            username='org1',
            email='org@test.com',
            password='pass123',
            user_type='ORG',
            organization_name='Test Corp'
        )
        
        self.client = Client()
    
    def test_applicant_can_follow_organization(self):
        self.client.login(username='applicant1', password='pass123')
        response = self.client.post(
            f'/organizations/follow/{self.org.id}/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertTrue(
            OrganizationFollow.objects.filter(
                user=self.applicant,
                organization=self.org,
                is_active=True
            ).exists()
        )
    
    def test_organization_cannot_follow(self):
        self.client.login(username='org1', password='pass123')
        response = self.client.post(
            f'/organizations/follow/{self.org.id}/'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_job_prioritization(self):
        # Create follow relationship
        OrganizationFollow.objects.create(
            user=self.applicant,
            organization=self.org,
            is_active=True
        )
        
        # Create jobs from followed and non-followed orgs
        # Test that followed org jobs appear first
        # ...
    
    # Add more tests...
```

---

## Future Enhancements

### Recommended Additions

1. **Email Notifications**
   - Send email when followed organization posts new job
   - Daily/weekly digest of jobs from followed organizations
   - Option to enable/disable notifications

2. **Follow Suggestions**
   - "Organizations you might like" based on:
     - Industry match
     - Location match
     - Jobs applied to
     - Popular organizations

3. **User Dashboard**
   - "My Followed Organizations" page
   - Manage all follows in one place
   - See stats: total follows, new jobs from follows
   - Unfollow multiple at once

4. **Rate Limiting**
   - Max 100 follow/unfollow actions per hour
   - Prevents spam and abuse
   - Implement using Django cache or rate-limit decorator

5. **Organization Insights**
   - Show organization how many followers they have
   - Follower growth chart
   - Follower demographics (location, experience level)

6. **Follow from Organization Profile**
   - Add follow button on organization profile page
   - Show follower list on organization profile

7. **Activity Feed**
   - "Recent activity from followed organizations"
   - Job postings, company updates, etc.

8. **Batch Operations**
   - Follow multiple organizations at once
   - Import follows from LinkedIn/other platforms

9. **Analytics**
   - Track follow/unfollow trends
   - Most followed organizations
   - Follow conversion rate (directory visit → follow)

10. **Export/Import**
    - Export followed organizations list
    - Import from CSV

---

## Troubleshooting

### Common Issues

**Issue:** Follow button not working
- **Solution:** Check browser console for JavaScript errors
- Ensure CSRF token is present in cookies
- Verify user is logged in and is an applicant

**Issue:** Jobs not prioritized correctly
- **Solution:** Check that `is_followed_org` is being annotated
- Verify ordering in queryset: `-is_followed_org, -created_at`
- Check that user is logged in and is applicant type

**Issue:** Follower count not updating
- **Solution:** Ensure AJAX response includes `follower_count`
- Check that JavaScript is updating the correct element
- Verify `.follower-count-{org_id}` class exists in HTML

**Issue:** Organization can access directory
- **Solution:** Check that view has proper user type check
- Ensure redirect is working correctly
- Verify middleware is not bypassing check

**Issue:** Duplicate follows created
- **Solution:** Check unique_together constraint in database
- Ensure migration was run successfully
- Verify clean() method in model is being called

---

## Database Queries Reference

### Get all organizations with follower count
```python
organizations = User.objects.filter(user_type='ORG').annotate(
    follower_count=Count('followers', filter=Q(followers__is_active=True))
)
```

### Check if user follows organization
```python
is_following = OrganizationFollow.objects.filter(
    user=user,
    organization=org,
    is_active=True
).exists()
```

### Get all followed organizations for user
```python
followed_orgs = User.objects.filter(
    followers__user=user,
    followers__is_active=True
)
```

### Get all jobs from followed organizations
```python
jobs = Job.objects.filter(
    posted_by__in=followed_orgs
).select_related('posted_by').order_by('-created_at')
```

### Get follower count for specific organization
```python
follower_count = OrganizationFollow.objects.filter(
    organization=org,
    is_active=True
).count()
```

---

## API Reference

### Follow Organization

**Endpoint:** `POST /organizations/follow/<org_id>/`

**Authentication:** Required (Applicant only)

**Parameters:**
- `org_id` (URL parameter): ID of organization to follow

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "You are now following Tech Corp",
    "follower_count": 145,
    "is_following": true
}
```

**Error Responses:**
```json
// 403 Forbidden
{
    "success": false,
    "error": "Only job seekers can follow organizations."
}

// 404 Not Found
{
    "success": false,
    "error": "Organization not found."
}

// 400 Bad Request
{
    "success": false,
    "error": "You are already following this organization."
}
```

---

### Unfollow Organization

**Endpoint:** `POST /organizations/unfollow/<org_id>/`

**Authentication:** Required (Applicant only)

**Parameters:**
- `org_id` (URL parameter): ID of organization to unfollow

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "You have unfollowed Tech Corp",
    "follower_count": 144,
    "is_following": false
}
```

**Error Responses:**
```json
// 403 Forbidden
{
    "success": false,
    "error": "Only job seekers can unfollow organizations."
}

// 404 Not Found
{
    "success": false,
    "error": "Organization not found."
}

// 400 Bad Request
{
    "success": false,
    "error": "You are not following this organization."
}
```

---

## Conclusion

This Organization Follow System provides a comprehensive solution for job seekers to discover and follow organizations, receiving prioritized job listings from companies they're interested in. The system is built with scalability, security, and user experience in mind.

For questions or issues, please refer to the troubleshooting section or contact the development team.

**Version:** 1.0  
**Last Updated:** December 25, 2025  
**Maintained By:** Payo Development Team
