# 🔐 Payo KYC System Documentation

## Overview
Complete KYC (Know Your Customer) verification system following Khalti/eSewa-style 3-step structure for both individual users and organizations.

---

## ✅ KYC Requirements

### Mandatory For:
- **Individual Users (Applicants)**: Cannot apply more than 2 jobs per day if NOT verified
- **Organizations**: Cannot post jobs unless KYC is approved

### Reminder + Block Rules:
- Unverified users see a sticky top banner: "Please complete your KYC to continue"
- Organizations: Job post button blocked until KYC verified
- Users: Limited to 2 job applications per day until verified
- Login required to fill KYC

---

## 🧩 KYC Form Structure (3 Steps)

### STEP 1 — Personal / Organization Basic Info

#### For Individual Users:
- Full Name *
- Date of Birth *
- Gender * (Male/Female/Other)
- Nationality *
- Marital Status * (Single/Married/Divorced/Widowed)
- Occupation *
- Education Level *
- Mobile Number * (10 digits)
- Email Address *
- Permanent Address * (Province → District → Municipality → Ward → Tole)
- Temporary Address

#### For Organizations:
- Organization Name *
- Registration Number *
- Registration Date *
- Type * (Company/Firm/NGO/School/Hospital/Other)
- PAN/VAT Number * (9 digits)
- Industry Type *
- Contact Number * (10 digits)
- Email Address *
- Registered Office Address *
- Current Operating Address

---

### STEP 2 — Identification & Documents Upload

#### For Individuals:
**Identification:**
- Citizenship Number *
- Issue Date *
- Issue District *
- Passport Number (optional)
- Driving License Number (optional)

**Document Uploads (Max 5MB each, JPG/PNG/PDF):**
- Citizenship Front * (JPG/PNG)
- Citizenship Back * (JPG/PNG)
- Recent Passport-Size Photo * (JPG/PNG)
- Address Proof * (citizenship/rent agreement/utility bill)
- Passport Photo (optional)
- Driving License (optional)

#### For Organizations:
**Document Uploads (Max 5MB each):**
- Registration Certificate * (PDF/JPG/PNG)
- PAN/VAT Certificate * (PDF/JPG/PNG)
- MOA/AA (Memorandum/Articles) (PDF)
- Partnership Agreement (if applicable) (PDF)
- Board Resolution (PDF)
- Office Address Verification * (utility bill/rent agreement)
- Authorized Signatory Citizenship * (JPG/PNG)
- Authorized Signatory Photo * (JPG/PNG)

---

### STEP 3 — Additional Verification + Declarations

#### For Individuals:
- Father's Name *
- Mother's Name *
- Grandfather's Name *
- Spouse's Name (if married)
- Expected Monthly Transaction * (dropdown)
- Annual Income Range * (dropdown)
- Purpose of Account * (default: "Apply Jobs, CV Screening")
- PEP (Politically Exposed Person) — Yes/No
- FATCA — Yes/No
- User Signature Upload (optional)
- **Declaration Checkbox * (mandatory)**

#### For Organizations:
- Major Shareholders Details (Name, %, Citizenship No.) - Optional, dynamic add
- Director(s) Information (Name, Contact) - Optional, dynamic add
- Authorized Person Declaration *
- Source of Funds *
- Expected Monthly Transaction Volume * (dropdown)
- PEP/FATCA Declaration
- Organization Stamp (optional)
- **Declaration Checkbox * (mandatory)**

---

## 📌 Backend Implementation

### Models (users/models.py)
- `User` model with `is_kyc_verified` flag
- `IndividualKYC` - All individual KYC fields
- `OrganizationKYC` - All organization KYC fields
- `KycAudit` - Audit trail for KYC actions

### Status Flow:
1. **DRAFT** - User is filling the form
2. **SUBMITTED** - User submitted for review
3. **VERIFIED** - Admin approved (user.is_kyc_verified = True)
4. **REJECTED** - Admin rejected with reason

### API Endpoints (api/views.py):
- `GET /api/kyc/` - Get user's KYC status
- `POST /api/kyc/` - Save KYC step data
- `PATCH /api/kyc/{type}/{id}/submit/` - Submit KYC for review
- `POST /api/kyc/{type}/{id}/admin_action/` - Admin verify/reject

### Forms (users/forms_kyc.py):
- `IndividualKYCStep1Form`, `IndividualKYCStep2Form`, `IndividualKYCStep3Form`
- `OrganizationKYCStep1Form`, `OrganizationKYCStep2Form`, `OrganizationKYCStep3Form`

### Validation Rules:
- Email must be valid format
- Phone number must be exactly 10 digits
- PAN must be exactly 9 digits
- Image uploads: JPG/PNG, max 5MB
- Document uploads: JPG/PNG/PDF, max 5MB
- Declaration checkbox mandatory in Step 3

---

## 🎨 Frontend Templates

### User-Facing:
- `/users/kyc/` - Main KYC form with 3-step wizard
- `templates/users/kyc_form.html` - Main form container
- `templates/users/kyc_individual_steps.html` - Individual form fields
- `templates/users/kyc_organization_steps.html` - Organization form fields
- `templates/includes/kyc_banner.html` - Reminder banner

### CMS (Admin):
- `/users/cms/` - CMS dashboard with filters
- `/users/cms/kyc/{type}/{id}/` - KYC detail & review page
- `templates/cms/dashboard.html` - Main CMS interface
- `templates/cms/kyc_detail.html` - KYC review interface

---

## 🔧 System Behavior

### Application Limits (Unverified Users):
```python
# In users/models.py
def can_apply_today(self):
    if self.is_kyc_verified:
        return True
    return self.get_daily_application_count() < 2
```

### Job Posting Restriction (Organizations):
```python
# In users/models.py
def can_post_jobs(self):
    return self.is_organization() and self.is_kyc_verified

# In organization/views.py - OrgJobCreateView
def dispatch(self, request, *args, **kwargs):
    if not request.user.can_post_jobs():
        messages.error(request, 'Please complete KYC verification to post jobs.')
        return redirect('/users/kyc/')
    return super().dispatch(request, *args, **kwargs)
```

### KYC Banner Display:
```python
# In users/models.py
def needs_kyc_banner(self):
    if self.is_kyc_verified:
        return False
    # Check if KYC exists and is not verified
    try:
        if self.is_applicant():
            kyc = IndividualKYC.objects.get(user=self)
            return kyc.status != 'VERIFIED'
        else:
            kyc = OrganizationKYC.objects.get(user=self)
            return kyc.status != 'VERIFIED'
    except:
        return True  # No KYC exists
```

---

## 📊 CMS Features

### Dashboard Tables:
1. **Users** - Filter by type, KYC status, date
2. **Jobs** - Filter by date, search
3. **Applications** - Filter by status, date
4. **KYC Records** - Filter by type, status, date

### KYC Review Actions:
- **Verify** - Approve KYC (sets user.is_kyc_verified = True)
- **Reject** - Reject with mandatory reason
- View all submitted documents
- See complete user/organization information

### Filters Available:
- Search (name, email, registration number)
- Status (Draft/Submitted/Verified/Rejected)
- Date range (from/to)
- User type (Applicant/Organization)
- KYC type (Individual/Organization)

---

## 🚀 Usage Flow

### For Users:
1. Sign up → See KYC banner
2. Click "Start KYC" → Redirected to `/users/kyc/`
3. Fill Step 1 → Click "Next" (auto-saves)
4. Fill Step 2 with documents → Click "Next"
5. Fill Step 3 + Declaration → Click "Submit for Review"
6. Status changes to "SUBMITTED"
7. Wait for admin approval (24-48 hours)

### For Organizations:
1. Sign up → Try to post job → Blocked
2. Redirected to KYC form
3. Complete 3-step organization KYC
4. Submit for review
5. After verification → Can post unlimited jobs

### For Admins:
1. Access CMS at `/users/cms/`
2. Click "KYC Records" tab
3. Filter by "SUBMITTED" status
4. Click "Review" on any KYC
5. View all details and documents
6. Click "Verify" or "Reject" with reason
7. User notified and status updated

---

## 🔒 Security Features

- CSRF protection on all forms
- File type validation (only JPG/PNG/PDF)
- File size limit (5MB max)
- Phone/PAN format validation
- Email format validation
- Login required for KYC access
- Staff-only access to CMS
- Audit trail for all KYC actions

---

## 📁 File Structure

```
Payo/
├── users/
│   ├── models.py                    # User, IndividualKYC, OrganizationKYC
│   ├── views.py                     # kyc_form_view, cms_dashboard, cms_kyc_detail
│   ├── forms_kyc.py                 # All KYC forms with validation
│   └── urls.py                      # /kyc/, /cms/, /cms/kyc/{type}/{id}/
├── api/
│   ├── views.py                     # KYC API endpoints
│   └── urls.py                      # /api/kyc/ endpoints
├── templates/
│   ├── users/
│   │   ├── kyc_form.html           # Main KYC form
│   │   ├── kyc_individual_steps.html
│   │   └── kyc_organization_steps.html
│   ├── cms/
│   │   ├── dashboard.html          # CMS main page
│   │   └── kyc_detail.html         # KYC review page
│   └── includes/
│       └── kyc_banner.html         # Reminder banner
└── media/
    └── kyc/
        ├── individual/             # Individual KYC uploads
        └── organization/           # Organization KYC uploads
```

---

## ✨ Key Features

✅ 3-step wizard with progress bar  
✅ Auto-save on each step  
✅ File upload with validation  
✅ Dynamic shareholder/director fields  
✅ Responsive design (mobile-friendly)  
✅ Real-time validation  
✅ Admin review interface  
✅ Audit trail  
✅ Email notifications (can be added)  
✅ Document preview in CMS  
✅ Status-based access control  

---

## 🎯 Testing Checklist

### User Flow:
- [ ] Individual user can access KYC form
- [ ] Organization user can access KYC form
- [ ] Step 1 saves correctly
- [ ] Step 2 accepts file uploads
- [ ] Step 3 requires declaration checkbox
- [ ] Submit button works
- [ ] Unverified user limited to 2 applications/day
- [ ] Organization blocked from posting jobs

### Admin Flow:
- [ ] CMS accessible to staff only
- [ ] KYC records display correctly
- [ ] Filters work (status, type, date)
- [ ] KYC detail page shows all info
- [ ] Documents are viewable
- [ ] Verify button works
- [ ] Reject button requires reason
- [ ] User.is_kyc_verified updates correctly

---

## 📞 Support

For issues or questions:
- Check models in `users/models.py`
- Check API endpoints in `api/views.py`
- Check forms in `users/forms_kyc.py`
- Check templates in `templates/users/` and `templates/cms/`

---

**System Status**: ✅ Fully Implemented  
**Last Updated**: 2025  
**Version**: 1.0
