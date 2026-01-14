# Organization Follow System - Quick Setup Guide

## ✅ Implementation Status: COMPLETE

All components of the Organization Follow System have been successfully implemented!

## What Was Implemented

### 1. Database Model ✅
- **File:** `organization/models.py`
- **Model:** `OrganizationFollow`
  - Tracks which applicants follow which organizations
  - Unique constraint prevents duplicate follows
  - Database indexes for performance
  - Validation to ensure only applicants can follow organizations

### 2. Views & Logic ✅
- **File:** `organization/views.py`

#### New Views:
1. `organizations_directory(request)`
   - Browse all organizations
   - Search and filter functionality
   - Pagination (20 per page)
   - Accessible to applicants only

2. `follow_organization(request, org_id)`
   - AJAX endpoint to follow an organization
   - Returns JSON response
   - Updates follower count

3. `unfollow_organization(request, org_id)`
   - AJAX endpoint to unfollow an organization
   - Returns JSON response
   - Updates follower count

#### Modified Views:
- **File:** `jobs/views.py`
- `JobListView` - Enhanced to prioritize jobs from followed organizations

### 3. URL Routing ✅
- **File:** `organization/urls.py`

New routes:
```python
path('directory/', organizations_directory, name='organizations-directory')
path('follow/<int:org_id>/', follow_organization, name='follow-organization')
path('unfollow/<int:org_id>/', unfollow_organization, name='unfollow-organization')
```

### 4. Templates ✅

#### New Templates:
1. **organizations_directory.html**
   - Location: `templates/organization/organizations_directory.html`
   - Features:
     - Organization cards grid
     - Search and filters
     - Follow/Unfollow buttons
     - Pagination
     - Login required modal
     - AJAX functionality

#### Modified Templates:
2. **job_list.html**
   - Location: `jobs/templates/jobs/job_list.html`
   - Features:
     - Organization info on each job card
     - Follow buttons on job cards
     - Section header for followed org jobs
     - Search and filter form
     - Link to organizations directory

### 5. Database Migration ✅
- Migration file created: `organization/migrations/0014_organizationfollow.py`
- Migration applied successfully
- Database table created: `organization_organizationfollow`

---

## How to Use the Feature

### For Job Seekers (Applicants)

#### 1. Browse Organizations
1. Navigate to `/organizations/directory/`
2. Or click "Browse Organizations" link (add to your navigation menu)
3. Use search box to find organizations by name
4. Use filters to narrow by industry or location
5. View organization details, follower count, job count

#### 2. Follow an Organization
1. Click the "Follow" button on any organization card
2. Button changes to "Following" with green checkmark
3. Follower count updates immediately
4. No page reload required (AJAX)

#### 3. Unfollow an Organization
1. Hover over "Following" button (turns red)
2. Click to unfollow
3. Button changes back to "Follow"
4. Follower count updates immediately

#### 4. See Prioritized Jobs
1. Navigate to `/jobs/` (job listings page)
2. Jobs from followed organizations appear at the top
3. Section header: "Jobs from Organizations You Follow"
4. Other jobs appear below

#### 5. Follow from Job Cards
1. On any job card, see organization info section
2. Click "Follow" button next to organization name
3. Button updates to "Following"
4. All instances of that organization update on the page
5. Stay on the job listings page (no redirect)

### For Organizations

- Organizations **cannot** access the organizations directory
- Attempting to access will redirect with error message
- Organizations **cannot** follow other organizations
- This feature is exclusively for job seekers

### For Logged-Out Users

- Can browse organizations directory
- Cannot follow organizations
- Clicking "Follow" shows login prompt/modal
- After login, returned to the same page

---

## Testing the Feature

### Quick Test Checklist

1. **As Logged-Out User:**
   - [ ] Visit `/organizations/directory/`
   - [ ] See all organizations displayed
   - [ ] Click "Follow" button → See login prompt
   - [ ] Search and filters work

2. **As Applicant:**
   - [ ] Visit `/organizations/directory/`
   - [ ] Follow an organization
   - [ ] See "Following" button
   - [ ] Visit `/jobs/`
   - [ ] See followed organization's jobs at top
   - [ ] Follow organization from job card
   - [ ] Unfollow from organizations directory
   - [ ] See button change to "Follow"

3. **As Organization:**
   - [ ] Visit `/organizations/directory/`
   - [ ] Get redirected with error message
   - [ ] Cannot access follow functionality

---

## Adding Navigation Links

To make the feature easily accessible, add these links to your navigation menu:

### For base2.html or navigation template:

```html
{% if user.is_authenticated and user.user_type == 'APP' %}
    <a href="{% url 'organization:organizations-directory' %}" class="nav-link">
        <i class="fas fa-building"></i> Organizations
    </a>
{% endif %}
```

### Example full navigation block:

```html
<!-- In your navbar -->
<nav class="navbar">
    <a href="{% url 'home' %}">Home</a>
    <a href="{% url 'jobs:list' %}">Jobs</a>
    
    {% if user.is_authenticated %}
        {% if user.user_type == 'APP' %}
            <!-- For Applicants -->
            <a href="{% url 'organization:organizations-directory' %}">
                <i class="fas fa-building"></i> Organizations
            </a>
            <a href="{% url 'users:profile' %}">My Profile</a>
        {% else %}
            <!-- For Organizations -->
            <a href="{% url 'organization:dashboard' %}">Dashboard</a>
            <a href="{% url 'organization:job-list' %}">My Jobs</a>
        {% endif %}
    {% else %}
        <a href="{% url 'users:login' %}">Login</a>
        <a href="{% url 'users:signup' %}">Sign Up</a>
    {% endif %}
</nav>
```

---

## Database Schema Diagram

```
┌─────────────────────────┐
│ OrganizationFollow      │
├─────────────────────────┤
│ id (PK)                 │
│ user_id (FK) → User     │ (Applicant)
│ organization_id (FK)    │ → User (Organization)
│ followed_at             │
│ is_active               │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│ Indexes                 │
├─────────────────────────┤
│ (user, organization)    │ UNIQUE
│ (user, is_active)       │
│ (organization, is_active)│
└─────────────────────────┘
```

---

## API Endpoints

### Follow Organization
```
POST /organizations/follow/<org_id>/
Authentication: Required (Applicant)

Response:
{
    "success": true,
    "message": "You are now following Tech Corp",
    "follower_count": 145,
    "is_following": true
}
```

### Unfollow Organization
```
POST /organizations/unfollow/<org_id>/
Authentication: Required (Applicant)

Response:
{
    "success": true,
    "message": "You have unfollowed Tech Corp",
    "follower_count": 144,
    "is_following": false
}
```

---

## File Checklist

All these files have been created/modified:

### New Files:
- ✅ `templates/organization/organizations_directory.html`
- ✅ `organization/migrations/0014_organizationfollow.py`
- ✅ `ORGANIZATION_FOLLOW_SYSTEM.md` (Full documentation)
- ✅ `ORGANIZATION_FOLLOW_SETUP.md` (This file)

### Modified Files:
- ✅ `organization/models.py` (Added OrganizationFollow model)
- ✅ `organization/views.py` (Added 3 new views, updated imports)
- ✅ `organization/urls.py` (Added 3 new URL patterns)
- ✅ `jobs/views.py` (Enhanced JobListView with prioritization)
- ✅ `jobs/templates/jobs/job_list.html` (Added follow buttons, org info)

---

## Performance Optimizations Applied

1. **Database Indexes**
   - Composite index on (user, is_active)
   - Composite index on (organization, is_active)
   - Speeds up follow status checks

2. **Query Optimization**
   - `select_related('posted_by')` - Reduces queries for job listings
   - `Count()` aggregation - Single query for follower counts
   - `Exists()` subquery - Efficient is_followed check
   - No N+1 query problems

3. **Caching Strategy (Future)**
   - Consider caching follower counts
   - Cache followed organization IDs for logged-in users
   - Use Redis for fast lookups

---

## Troubleshooting

### Common Issues & Solutions

**Problem:** Follow button not working
- Check browser console for JavaScript errors
- Verify CSRF token in cookies
- Ensure user is logged in as applicant

**Problem:** Jobs not prioritized
- Verify user is logged in as applicant
- Check that followed organizations exist
- Review queryset ordering in JobListView

**Problem:** Template not found error
- Ensure template is in correct location
- Check TEMPLATES setting in settings.py
- Verify app is in INSTALLED_APPS

**Problem:** Migration fails
- Check for existing OrganizationFollow model
- Delete migration and recreate if needed
- Ensure database is accessible

---

## Next Steps

### Immediate (Optional):
1. **Add navigation links** to organizations directory
2. **Test all functionality** with real users
3. **Add CSS customization** to match your theme

### Future Enhancements:
1. Email notifications when followed org posts job
2. "Organizations you might like" suggestions
3. Follower analytics for organizations
4. Export/import followed organizations
5. Rate limiting on follow/unfollow actions
6. Activity feed from followed organizations

---

## Support

For detailed information, see `ORGANIZATION_FOLLOW_SYSTEM.md`

For questions or issues:
1. Check the troubleshooting section above
2. Review the full documentation
3. Check browser console for errors
4. Verify all files are in correct locations

---

## Summary

✅ **Model Created** - OrganizationFollow with proper relationships  
✅ **Views Implemented** - 3 new views + 1 modified  
✅ **Templates Created** - 1 new + 1 modified  
✅ **URLs Configured** - 3 new routes  
✅ **Migration Applied** - Database table created  
✅ **JavaScript Added** - AJAX follow/unfollow functionality  
✅ **Permissions Set** - Access control for applicants only  
✅ **Documentation Written** - Full guide + quick setup  

**The feature is now ready to use!** 🎉

Navigate to `/organizations/directory/` to start using the Organization Follow System.
