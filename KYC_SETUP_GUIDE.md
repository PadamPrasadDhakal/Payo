# 🚀 KYC System Setup Guide

## Quick Start

### 1. Database Migrations
The KYC models are already in your database from previous migrations. If you need to apply any new changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Media Directories
Ensure media directories exist for file uploads:

```bash
mkdir -p media/kyc/individual/citizenship
mkdir -p media/kyc/individual/passport
mkdir -p media/kyc/individual/license
mkdir -p media/kyc/individual/photos
mkdir -p media/kyc/individual/address
mkdir -p media/kyc/individual/signatures
mkdir -p media/kyc/organization/registration
mkdir -p media/kyc/organization/pan
mkdir -p media/kyc/organization/moa
mkdir -p media/kyc/organization/partnership
mkdir -p media/kyc/organization/resolution
mkdir -p media/kyc/organization/address
mkdir -p media/kyc/organization/signatory
mkdir -p media/kyc/organization/stamps
```

### 3. Create Admin User (if not exists)
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

---

## 🧪 Testing the System

### Test as Individual User:
1. Go to `http://localhost:8000/users/signup/`
2. Select "Job Applier" (Applicant)
3. Complete registration
4. Login and you'll see KYC banner
5. Click "Complete KYC Now"
6. Fill all 3 steps and submit
7. Try applying to jobs (limited to 2/day until verified)

### Test as Organization:
1. Go to `http://localhost:8000/users/signup/`
2. Select "Organization"
3. Complete registration
4. Login and you'll see KYC banner
5. Try to post a job → redirected to KYC
6. Complete KYC form (all 3 steps)
7. Submit for review

### Test as Admin:
1. Login to admin panel: `http://localhost:8000/admin/`
2. Or go to CMS: `http://localhost:8000/users/cms/`
3. Select "KYC Records" from dropdown
4. Filter by "SUBMITTED" status
5. Click on a KYC record
6. Review all details and documents
7. Click "Verify" or "Reject" with reason

---

## 📋 URLs Reference

### User URLs:
- **KYC Form**: `/users/kyc/`
- **Dashboard**: `/users/dashboard/`
- **Applications**: `/users/applications/`
- **Profile**: `/users/profile/`

### Admin URLs:
- **CMS Dashboard**: `/users/cms/`
- **KYC Detail**: `/users/cms/kyc/{type}/{id}/`
- **Django Admin**: `/admin/`

### API URLs:
- **List/Create KYC**: `/api/kyc/`
- **KYC Detail**: `/api/kyc/{type}/{id}/`
- **Submit KYC**: `/api/kyc/{type}/{id}/submit/`
- **Admin Action**: `/api/kyc/{type}/{id}/admin_action/`

---

## 🔍 Verification Checklist

### Individual KYC Verification:
- [ ] Full name matches citizenship
- [ ] Date of birth is valid
- [ ] Citizenship number is clear and readable
- [ ] Citizenship front/back images are clear
- [ ] Recent photo is passport-size
- [ ] Address proof is valid
- [ ] All required fields filled
- [ ] Declaration accepted

### Organization KYC Verification:
- [ ] Organization name matches registration
- [ ] Registration number is valid
- [ ] PAN/VAT number is 9 digits
- [ ] Registration certificate is clear
- [ ] PAN/VAT certificate is valid
- [ ] MOA/AA document provided
- [ ] Board resolution is signed
- [ ] Signatory documents are clear
- [ ] All required fields filled
- [ ] Declaration accepted

---

## ⚠️ Common Issues & Solutions

### Issue: "File too large" error
**Solution**: Ensure files are under 5MB. Compress images if needed.

### Issue: KYC banner not showing
**Solution**: Check that user is logged in and `is_kyc_verified=False`

### Issue: Can't post jobs (organization)
**Solution**: Complete KYC and wait for admin verification

### Issue: Application limit reached
**Solution**: Complete KYC to remove 2/day limit, or wait until next day

### Issue: Documents not uploading
**Solution**: 
- Check file format (JPG/PNG for images, PDF for documents)
- Ensure media directory has write permissions
- Check MEDIA_ROOT and MEDIA_URL in settings.py

### Issue: CMS not accessible
**Solution**: Ensure user has `is_staff=True` permission

---

## 🎯 Testing Scenarios

### Scenario 1: New User Registration
1. Register as applicant
2. See KYC banner
3. Try to apply to 3 jobs → blocked after 2
4. Complete KYC
5. Apply to unlimited jobs after verification

### Scenario 2: Organization Job Posting
1. Register as organization
2. Try to post job → redirected to KYC
3. Complete KYC form
4. Submit for review
5. Admin verifies
6. Can now post jobs

### Scenario 3: KYC Rejection
1. User submits incomplete KYC
2. Admin reviews and rejects with reason
3. User sees rejection reason
4. User can edit and resubmit
5. Admin verifies on second attempt

### Scenario 4: Admin Review Workflow
1. Multiple KYC submissions pending
2. Admin filters by "SUBMITTED" status
3. Reviews each one systematically
4. Verifies valid ones
5. Rejects invalid ones with clear reasons
6. Users get instant status updates

---

## 📊 Database Queries (for debugging)

### Check KYC Status:
```python
from users.models import User, IndividualKYC, OrganizationKYC

# Get user's KYC
user = User.objects.get(username='testuser')
print(user.is_kyc_verified)
print(user.get_kyc_status())

# Get all pending KYCs
pending_individual = IndividualKYC.objects.filter(status='SUBMITTED')
pending_org = OrganizationKYC.objects.filter(status='SUBMITTED')
```

### Check Application Count:
```python
from organization.models import Application
from django.utils import timezone

user = User.objects.get(username='testuser')
today = timezone.now().date()
count = Application.objects.filter(applicant=user, created_at__date=today).count()
print(f"Applications today: {count}")
```

### Manually Verify KYC (for testing):
```python
user = User.objects.get(username='testuser')
user.is_kyc_verified = True
user.save()

# Or through KYC model
kyc = IndividualKYC.objects.get(user=user)
kyc.status = 'VERIFIED'
kyc.save()
```

---

## 🔐 Security Notes

1. **File Storage**: All uploaded files stored in `media/kyc/`
2. **Access Control**: Users can only view their own KYC
3. **Admin Only**: CMS requires `is_staff=True`
4. **CSRF Protection**: All forms use CSRF tokens
5. **Validation**: Both client and server-side validation
6. **Audit Trail**: All admin actions logged in KycAudit table

---

## 📈 Monitoring

### Check System Health:
```python
# Total KYC submissions
from users.models import IndividualKYC, OrganizationKYC

total_individual = IndividualKYC.objects.count()
total_org = OrganizationKYC.objects.count()
verified = IndividualKYC.objects.filter(status='VERIFIED').count() + OrganizationKYC.objects.filter(status='VERIFIED').count()
pending = IndividualKYC.objects.filter(status='SUBMITTED').count() + OrganizationKYC.objects.filter(status='SUBMITTED').count()

print(f"Total KYCs: {total_individual + total_org}")
print(f"Verified: {verified}")
print(f"Pending Review: {pending}")
```

---

## 🎓 Training for Admins

### KYC Review Best Practices:
1. **Check Document Clarity**: Ensure all images/PDFs are readable
2. **Verify Information**: Cross-check details across documents
3. **Look for Red Flags**: Mismatched names, dates, or numbers
4. **Provide Clear Reasons**: When rejecting, be specific about issues
5. **Be Consistent**: Apply same standards to all submissions
6. **Review Thoroughly**: Don't rush through verifications
7. **Document Issues**: Use rejection reason field effectively

### Common Rejection Reasons:
- "Citizenship image is blurry/unreadable"
- "PAN number doesn't match certificate"
- "Registration certificate is expired"
- "Missing required document: [document name]"
- "Name mismatch between documents"
- "Address proof is not valid (must be utility bill/rent agreement)"
- "Organization stamp is not clear"
- "Signatory citizenship is incomplete"

---

## 🚀 Production Deployment

### Before Going Live:
1. [ ] Set `DEBUG = False` in settings.py
2. [ ] Configure proper MEDIA_ROOT and MEDIA_URL
3. [ ] Set up file storage (AWS S3 recommended)
4. [ ] Enable HTTPS for secure file uploads
5. [ ] Set up backup for media files
6. [ ] Configure email notifications for KYC status
7. [ ] Set up monitoring and logging
8. [ ] Train admin staff on review process
9. [ ] Create admin documentation
10. [ ] Test all workflows end-to-end

---

## 📞 Support

For technical issues:
- Check Django logs: `python manage.py runserver` output
- Check browser console for JavaScript errors
- Review database for data integrity
- Check file permissions on media directory

---

**Setup Complete!** 🎉

Your KYC system is now ready to use. Test thoroughly before deploying to production.
