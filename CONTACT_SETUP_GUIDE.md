# Contact Form Setup Guide

## Overview
The contact form has been successfully implemented with the following features:
- User-friendly form with validation
- Multiple predefined query types
- Custom query option
- Email notifications to admin and user
- Success message with "Send Another Query" option

## Features Implemented

### 1. Contact Form Fields
- **Name**: Full name of the user (required)
- **Email**: Email address for replies (required)
- **Phone**: Contact number (required)
- **Query Type**: Dropdown with predefined options (required)
  - General Inquiry
  - Technical Support
  - Job Posting
  - Account Issues
  - Payment & Billing
  - Partnership
  - Feedback
  - Custom Query (shows additional text field)
- **Message**: Detailed query description (required)

### 2. Email Functionality
- Sends email to admin with query details
- Sends confirmation email to user
- Error handling for email failures

### 3. Success Flow
After successful submission:
- Shows success message
- Displays "Send Another Query" button
- Displays "Back to Home" button

## Configuration

### Current Setup (Development)
The email backend is set to **console** mode, which means emails will be printed in the terminal/console instead of being sent. This is perfect for testing.

### Production Setup
To enable actual email sending in production:

1. **Open** `JobsHaruPrj/settings.py`

2. **Update the email configuration** (around line 145):
   ```python
   # Change from console to SMTP
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
   EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
   ```

3. **Create/Update `.env` file** in the project root:
   ```env
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=noreply@jobsharu.com
   CONTACT_EMAIL=support@jobsharu.com
   ```

### Gmail Setup (if using Gmail)
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an "App Password":
   - Go to Google Account Settings
   - Security → 2-Step Verification
   - App passwords → Generate new password
   - Use this password in `.env` file

### Alternative Email Services
- **SendGrid**: Set `EMAIL_HOST = 'smtp.sendgrid.net'` and `EMAIL_PORT = 587`
- **Mailgun**: Set `EMAIL_HOST = 'smtp.mailgun.org'` and `EMAIL_PORT = 587`
- **AWS SES**: Set `EMAIL_HOST = 'email-smtp.region.amazonaws.com'`

## Testing

### Development Testing
1. Start the Django server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to: `http://localhost:8000/contact/`

3. Fill out and submit the form

4. Check the **terminal/console** where Django is running - you'll see the email content printed there

### Production Testing
1. Configure SMTP settings (see above)
2. Submit a test query
3. Check your email inbox for confirmation
4. Check admin email for the query details

## Files Modified

1. **templates/contact.html** - Complete contact form UI
2. **JobsHaruPrj/views.py** - Added `contact_view()` function
3. **JobsHaruPrj/urls.py** - Updated contact URL to use view
4. **JobsHaruPrj/settings.py** - Added email configuration

## Customization

### Change Query Types
Edit `templates/contact.html` around line 45-54 to add/remove query types:
```html
<option value="Your New Type">Your New Type</option>
```

### Change Admin Email
Update `CONTACT_EMAIL` in `settings.py` or set in `.env` file

### Customize Email Content
Edit the `contact_view()` function in `JobsHaruPrj/views.py` around lines 47-85

## Troubleshooting

### Emails not sending
- Check email configuration in settings.py
- Verify credentials in .env file
- Check firewall/antivirus blocking SMTP port
- Look for errors in Django console

### Form not submitting
- Check browser console for JavaScript errors
- Verify CSRF token is present
- Check Django server logs

### Success page not showing
- Verify the view is returning `{'success': True}`
- Check template conditional logic

## Security Notes
- Never commit `.env` file with real credentials to version control
- Use app-specific passwords, not your main email password
- Consider rate limiting for production to prevent spam
- Add CAPTCHA for additional security (optional)
