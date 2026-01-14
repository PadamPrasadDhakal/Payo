# Organization Follow System - Quick Reference

## URLs

```python
# Browse organizations
/organizations/directory/

# Follow API
POST /organizations/follow/<org_id>/

# Unfollow API
POST /organizations/unfollow/<org_id>/
```

## Django Template Tags

```django
{# Check if user follows organization #}
{% if org_id in followed_org_ids %}
    <button>Following</button>
{% else %}
    <button>Follow</button>
{% endif %}

{# Link to organizations directory #}
<a href="{% url 'organization:organizations-directory' %}">Organizations</a>

{# Follow button #}
<a href="{% url 'organization:follow-organization' org.id %}">Follow</a>
```

## JavaScript Functions

```javascript
// Follow organization
followOrganization(orgId)

// Unfollow organization
unfollowOrganization(orgId)

// Follow from job card (updates all instances)
followOrganizationFromJob(orgId)

// Unfollow from job card
unfollowOrganizationFromJob(orgId)

// Show toast notification
showToast('success', 'Message here')
showToast('error', 'Error message')
```

## Python/Django Usage

```python
# Get all followers of an organization
followers = OrganizationFollow.objects.filter(
    organization=org,
    is_active=True
)

# Get all organizations a user follows
followed_orgs = OrganizationFollow.objects.filter(
    user=user,
    is_active=True
).values_list('organization', flat=True)

# Check if user follows organization
is_following = OrganizationFollow.objects.filter(
    user=user,
    organization=org,
    is_active=True
).exists()

# Get follower count
follower_count = OrganizationFollow.objects.filter(
    organization=org,
    is_active=True
).count()

# Create follow
OrganizationFollow.objects.create(
    user=user,
    organization=org,
    is_active=True
)

# Unfollow (deactivate)
follow = OrganizationFollow.objects.get(
    user=user,
    organization=org
)
follow.is_active = False
follow.save()
```

## Database Queries

```python
# Get organizations with follower count
from django.db.models import Count, Q

orgs = User.objects.filter(user_type='ORG').annotate(
    follower_count=Count('followers', filter=Q(followers__is_active=True))
)

# Get jobs from followed organizations (prioritized)
from django.db.models import Exists, OuterRef

jobs = Job.objects.annotate(
    is_followed_org=Exists(
        OrganizationFollow.objects.filter(
            user=request.user,
            organization=OuterRef('posted_by'),
            is_active=True
        )
    )
).order_by('-is_followed_org', '-created_at')
```

## CSS Classes

```css
/* Follow buttons */
.btn-follow         /* Not following */
.btn-following      /* Already following */
.btn-loading        /* During API call */
.btn-follow-sm      /* Small version for job cards */
.btn-following-sm   /* Small following button */

/* Organization cards */
.organization-card
.org-logo-container
.org-logo
.org-logo-placeholder
.org-card-body
.org-name
.org-meta
.org-description
.org-stats
.org-actions
```

## Permissions

```python
# Only applicants can:
- Access organizations directory
- Follow/unfollow organizations
- See prioritized job listings

# Organizations cannot:
- Access organizations directory (redirected)
- Follow other organizations (403 error)
- Use any follow features

# Logged-out users can:
- Browse organizations directory
- View job listings (normal order)
- See organization profiles

# Logged-out users cannot:
- Follow organizations (login required)
- See prioritized jobs
```

## Common Code Snippets

### Add follow button to any page
```django
{% if user.is_authenticated and user.user_type == 'APP' %}
    {% if is_following %}
        <button onclick="unfollowOrganization({{ org.id }})">
            <i class="fas fa-check"></i> Following
        </button>
    {% else %}
        <button onclick="followOrganization({{ org.id }})">
            <i class="fas fa-plus"></i> Follow
        </button>
    {% endif %}
{% endif %}
```

### Get follow status in view
```python
def my_view(request, org_id):
    organization = User.objects.get(id=org_id, user_type='ORG')
    
    is_following = False
    if request.user.is_authenticated and request.user.user_type == 'APP':
        is_following = OrganizationFollow.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True
        ).exists()
    
    context = {
        'organization': organization,
        'is_following': is_following,
    }
    return render(request, 'template.html', context)
```

### AJAX follow request
```javascript
fetch(`/organizations/follow/${orgId}/`, {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json',
    },
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        // Update UI
        console.log('Follower count:', data.follower_count);
    }
});
```

## Model Fields Reference

```python
OrganizationFollow:
    - id: AutoField (Primary Key)
    - user: ForeignKey to User (applicant)
    - organization: ForeignKey to User (organization)
    - followed_at: DateTimeField (auto_now_add)
    - is_active: BooleanField (default True)
    
Constraints:
    - unique_together: (user, organization)
    
Indexes:
    - (user, is_active)
    - (organization, is_active)
```

## HTTP Response Codes

- `200` - Success
- `400` - Bad request (already following, etc.)
- `401` - Unauthorized (not logged in)
- `403` - Forbidden (wrong user type)
- `404` - Not found (organization doesn't exist)

## JSON Response Format

```json
{
    "success": true,
    "message": "You are now following Tech Corp",
    "follower_count": 145,
    "is_following": true
}
```

## Debug Commands

```bash
# Check OrganizationFollow records
python manage.py shell
>>> from organization.models import OrganizationFollow
>>> OrganizationFollow.objects.all()
>>> OrganizationFollow.objects.filter(is_active=True).count()

# Check followed organizations for a user
>>> from users.models import User
>>> user = User.objects.get(username='applicant1')
>>> user.following_organizations.filter(is_active=True)

# Check followers of an organization
>>> org = User.objects.get(id=5, user_type='ORG')
>>> org.followers.filter(is_active=True).count()
```

## File Locations

```
organization/
├── models.py                    # OrganizationFollow model
├── views.py                     # 3 new views
├── urls.py                      # 3 new routes
└── migrations/
    └── 0014_organizationfollow.py

jobs/
├── views.py                     # Modified JobListView
└── templates/
    └── jobs/
        └── job_list.html        # Enhanced with follow buttons

templates/
└── organization/
    └── organizations_directory.html  # New template

ORGANIZATION_FOLLOW_SYSTEM.md    # Full documentation
ORGANIZATION_FOLLOW_SETUP.md     # Setup guide
ORGANIZATION_FOLLOW_QUICK_REF.md # This file
```

---

**For complete details, see:** `ORGANIZATION_FOLLOW_SYSTEM.md`
