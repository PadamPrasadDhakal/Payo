# Unified Notification System - Implementation Guide

## Overview
The Payo platform now features a fully unified notification system that merges general notifications, hiring/selection notifications, and all other notification types into a single, streamlined system.

## ✨ Features Implemented

### 1. **Unified Notification Model**
- Single `Notification` model handles all notification types
- Comprehensive notification types including:
  - **KYC Notifications**: Verified, Rejected, Submitted, More Info Required
  - **Application Status**: Submitted, Reviewed, Shortlisted, Selected, Hired, Rejected
  - **Job Related**: Posted, Matched
  - **Organization Notifications**: New Application, Interest Received, Profile Viewed
  - **Communication**: Message Received
  - **System**: Announcements, General

### 2. **Notification Center** (`/users/notifications/`)
- Modern, responsive UI with Tailwind CSS
- Advanced filtering by:
  - Notification Type (Applications, KYC, Organization, etc.)
  - Read/Unread Status
- Pagination (15 notifications per page)
- Bulk actions:
  - Mark all as read
  - Delete all read notifications
- Individual notification actions:
  - Mark as read
  - Delete notification
  - Click to navigate to related page

### 3. **5-Second Popup Notifications**
- Automatic popup for new notifications
- **Auto-dismiss after 5 seconds**
- Features:
  - Smooth slide-in/slide-out animations
  - Progress bar showing remaining time
  - Hover to pause auto-dismiss
  - Click to navigate to related page
  - Manual dismiss with close button
  - Queue system for multiple notifications
  - Maximum 3 popups shown simultaneously
- Color-coded by notification type
- Icon-based visual identification

### 4. **Real-time Updates**
- Polling system checks for new notifications every 10 seconds
- Automatic badge count updates
- Pauses when tab is inactive (resource-efficient)
- Resumes and checks immediately when user returns

### 5. **API Endpoints**

#### **GET** `/users/api/notifications/recent/`
Returns recent unread notifications for popup system
```json
{
  "success": true,
  "notifications": [
    {
      "id": 123,
      "title": "You've been Selected!",
      "message": "Congratulations! You've been selected for...",
      "type": "APP_SELECTED",
      "icon": "🎉",
      "is_read": false,
      "created_at": "2025-12-21T12:30:00Z",
      "action_url": "/users/applications/?highlight=456"
    }
  ],
  "count": 1,
  "total_unread": 5
}
```

#### **GET** `/users/api/notifications/unread-count/`
Returns count of unread notifications
```json
{
  "success": true,
  "unread_count": 5
}
```

#### **POST** `/users/notifications/`
Actions: `mark_read`, `mark_all_read`, `delete`, `delete_all_read`

### 6. **Automatic Notification Triggers**

Notifications are automatically created when:

#### Application Status Changes (Organization → Applicant)
- **Reviewing**: "Application Under Review"
- **Shortlisted**: "🎯 You've been Shortlisted!"
- **Selected**: "🎉 You've been Selected!"
- **Hired**: "🎊 You're Hired!"
- **Rejected**: "Application Update" (gentle message)

#### KYC Updates (System → User)
- **Verified**: "KYC Verification Approved ✓"
- **Rejected**: "KYC Verification Rejected ✗"

#### Express Interest (Applicant → Organization)
- "💚 New interest in your Top Users listing"

## 🔧 Technical Implementation

### Model Updates
**File**: `users/models.py`
- Added `action_url` field for click-to-navigate
- Added helper methods:
  - `get_icon()`: Returns emoji icon for notification type
  - `get_color_class()`: Returns Tailwind classes for styling

### Views & APIs
**File**: `users/views.py`
- Enhanced `notifications()` view with filtering
- New `notifications_api()` for popup system
- Actions: mark read, delete, bulk operations

### Organization Integration
**File**: `organization/views.py`
- `update_application_status()` now creates notifications
- Status-specific messages and icons
- Includes navigation URLs

### Frontend Components

#### Notification Popup System
**File**: `templates/includes/notification_popup.html`
- Self-contained JavaScript notification system
- Automatic polling and display
- Queue management
- Responsive animations

#### Notification Center
**File**: `templates/users/notifications.html`
- Filter dropdowns
- Pagination
- AJAX actions
- Responsive card layout

#### Base Templates
Updated: `base.html`, `base2.html`, `org_base.html`
- Included popup system
- Notification bell icon
- Badge counter

## 📋 Usage Guide

### For Developers

#### Creating a Notification Programmatically
```python
from users.models import Notification

# Create notification
Notification.objects.create(
    user=target_user,
    title='🎉 Congratulations!',
    message='You have achieved something great!',
    notification_type='GENERAL',  # or APP_SELECTED, KYC_VERIFIED, etc.
    related_id=related_object_id,  # Optional
    action_url='/path/to/navigate/'  # Optional
)
```

#### Notification Types Available
```python
NOTIFICATION_TYPES = [
    'KYC_VERIFIED', 'KYC_REJECTED', 'KYC_SUBMITTED', 'KYC_MORE_INFO',
    'APP_SUBMITTED', 'APP_REVIEWED', 'APP_SHORTLISTED', 'APP_SELECTED', 
    'APP_HIRED', 'APP_REJECTED',
    'JOB_POSTED', 'JOB_MATCHED',
    'NEW_APPLICATION', 'INTEREST_RECEIVED', 'PROFILE_VIEWED',
    'MESSAGE_RECEIVED',
    'SYSTEM_ANNOUNCEMENT', 'GENERAL'
]
```

### For Users

#### Viewing Notifications
1. Click the bell icon in the navigation bar
2. Access full notification center at `/users/notifications/`
3. Popups appear automatically for new notifications

#### Managing Notifications
- **Mark as Read**: Click the "✓ Mark Read" button
- **Delete**: Click the "🗑️ Delete" button
- **Filter**: Use dropdown filters for type and status
- **Bulk Actions**: "Mark all as read" or "Delete Read" buttons

## 🎨 Styling & Customization

### Color Coding
Each notification type has distinct colors:
- **Selected/Hired**: Green
- **Shortlisted**: Purple
- **Rejected**: Red
- **New Application**: Blue
- **Interest**: Pink
- **Announcements**: Yellow
- **General**: Gray

### Icons
Every notification type has a unique emoji icon for quick visual identification.

## 🧪 Testing

### Test Flow
1. **Login as Organization**
2. **Post a job** or use existing job
3. **Change application status** (Shortlisted, Selected, Hired)
4. **Login as Applicant** (the user whose status was changed)
5. **Observe**:
   - Popup notification appears automatically (5-second timer)
   - Bell icon shows unread count
   - Notification center lists all notifications
6. **Test Actions**:
   - Hover popup → timer pauses
   - Click popup → navigates to applications
   - Click "Mark Read" → notification styling updates
   - Use filters → notifications filter correctly

### KYC Notification Test
1. Submit KYC verification
2. Admin approves/rejects KYC
3. User receives notification automatically

### Manual Notification Creation (Admin)
```python
# Django shell
python manage.py shell

from users.models import User, Notification
user = User.objects.get(username='testuser')

Notification.objects.create(
    user=user,
    title='Test Notification',
    message='This is a test popup notification',
    notification_type='GENERAL'
)
```

## 📊 Performance Considerations

### Optimizations Implemented
- **Polling Pause**: Stops when tab is inactive
- **Indexed Queries**: Database indexes on `user` and `is_read`
- **Pagination**: Prevents loading too many notifications
- **Queue System**: Limits simultaneous popups to 3
- **Efficient Updates**: Only polls for new notifications since last check

### Database Indexes
```python
indexes = [
    models.Index(fields=['user', '-created_at']),
    models.Index(fields=['user', 'is_read']),
]
```

## 🔮 Future Enhancements

Possible improvements:
1. **WebSocket Integration** - Replace polling with Django Channels for true real-time
2. **Push Notifications** - Browser push notifications when tab is closed
3. **Email Notifications** - Send email for important notifications
4. **Notification Preferences** - Let users choose which types they want
5. **Sound Alerts** - Optional sound for new notifications
6. **Mobile App Integration** - Push to mobile devices

## 🐛 Troubleshooting

### Popups Not Appearing
- Check browser console for JavaScript errors
- Ensure user is authenticated
- Verify `/users/api/notifications/recent/` endpoint is accessible
- Check notification popup container exists in HTML

### Badge Count Not Updating
- Verify `/users/api/notifications/unread-count/` endpoint works
- Check browser console for fetch errors
- Ensure CSRF token is present

### Notifications Not Created
- Check application status is actually changing
- Verify Notification model import in views
- Check database for notification records
- Look at server logs for errors

## 📝 Files Modified/Created

### New Files
- `templates/includes/notification_popup.html` - Popup system
- `templates/users/notifications.html` - Enhanced notification center
- `NOTIFICATION_SYSTEM.md` - This documentation

### Modified Files
- `users/models.py` - Enhanced Notification model
- `users/views.py` - Added APIs and filtering
- `users/urls.py` - Added new routes
- `organization/views.py` - Added notification triggers
- `templates/base.html` - Included popup system
- `templates/base2.html` - Included popup system
- `templates/org_base.html` - Included popup system

## ✅ Success Criteria Met

- ✅ Merged general and hiring notifications into one system
- ✅ Created unified notification center with filtering
- ✅ Implemented 5-second auto-dismiss popups
- ✅ Added notification triggers for application status changes
- ✅ Proper color coding and icons for all types
- ✅ Click-to-navigate functionality
- ✅ Bulk operations (mark all read, delete read)
- ✅ Real-time polling with performance optimization
- ✅ Mobile-responsive UI
- ✅ Smooth animations and transitions

## 🎯 Conclusion

The unified notification system provides a comprehensive, user-friendly way to keep users informed about all important updates. The system is extensible, performant, and follows Django and Tailwind CSS best practices.

For questions or issues, check the troubleshooting section or review the implementation files listed above.
