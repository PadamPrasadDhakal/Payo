# 🔐 KYC System - Quick Reference Card

## 🎯 System Rules

| User Type | Without KYC | With KYC |
|-----------|-------------|----------|
| **Individual** | Max 2 job applications/day | Unlimited applications |
| **Organization** | Cannot post jobs | Can post unlimited jobs |

---

## 📝 KYC Status Flow

```
┌─────────┐     ┌───────────┐     ┌──────────┐
│  DRAFT  │ --> │ SUBMITTED │ --> │ VERIFIED │
└─────────┘     └───────────┘     └──────────┘
                      │
                      v
                ┌──────────┐
                │ REJECTED │
                └──────────┘
```

---

## 🔗 Quick Links

### User URLs
```
/users/kyc/                    → KYC Form
/users/dashboard/              → User Dashboard
/users/applications/           → My Applications
```

### Admin URLs
```
/users/cms/                    → CMS Dashboard
/users/cms/kyc/{type}/{id}/    → Review KYC
/admin/                        → Django Admin
```

### API Endpoints
```
GET  /api/kyc/                 → Get KYC status
POST /api/kyc/                 → Save step data
PATCH /api/kyc/{type}/{id}/submit/  → Submit for review
POST /api/kyc/{type}/{id}/admin_action/  → Verify/Reject
```

---

## 📋 Required Fields Summary

### Individual (Step 1)
✅ Full Name, DOB, Gender, Nationality, Marital Status, Occupation, Education, Mobile (10 digits), Email, Permanent Address

### Individual (Step 2)
✅ Citizenship No., Issue Date, Issue District
📄 Citizenship Front/Back, Recent Photo, Address Proof

### Individual (Step 3)
✅ Father/Mother/Grandfather Name, Monthly Transaction, Annual Income, Purpose
☑️ Declaration Checkbox

### Organization (Step 1)
✅ Org Name, Registration No., Registration Date, Type, PAN/VAT (9 digits), Industry, Contact (10 digits), Email, Addresses

### Organization (Step 2)
📄 Registration Cert, PAN/VAT Cert, MOA/AA, Board Resolution, Address Verification, Signatory Citizenship/Photo

### Organization (Step 3)
✅ Shareholders, Directors, Declaration, Source of Funds, Transaction Volume
📄 Organization Stamp
☑️ Declaration Checkbox

---

## ⚡ Validation Rules

| Field | Rule |
|-------|------|
| Email | Valid email format |
| Mobile | Exactly 10 digits |
| PAN/VAT | Exactly 9 digits |
| Images | JPG/PNG, max 5MB |
| Documents | JPG/PNG/PDF, max 5MB |
| Declaration | Must be checked |

---

## 🎨 Status Colors

| Status | Color | Badge |
|--------|-------|-------|
| DRAFT | Gray | 🔘 |
| SUBMITTED | Blue | 📤 |
| VERIFIED | Green | ✅ |
| REJECTED | Red | ❌ |

---

## 🔧 Admin Actions

### Verify KYC
```javascript
POST /api/kyc/{type}/{id}/admin_action/
{
  "status": "VERIFIED",
  "reason": "All documents verified"
}
```

### Reject KYC
```javascript
POST /api/kyc/{type}/{id}/admin_action/
{
  "status": "REJECTED",
  "reason": "Citizenship image is unclear"
}
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Banner not showing | Check `user.is_kyc_verified` is False |
| Can't upload files | Check file size (<5MB) and format |
| Application limit | Complete KYC or wait until next day |
| Can't post jobs | Complete organization KYC |
| CMS not accessible | User needs `is_staff=True` |

---

## 📊 Database Models

```python
# Check user KYC status
user.is_kyc_verified          # Boolean
user.get_kyc_status()         # Dict with type, status, step
user.needs_kyc_banner()       # Boolean
user.can_apply_today()        # Boolean (for applicants)
user.can_post_jobs()          # Boolean (for organizations)

# Get KYC record
IndividualKYC.objects.get(user=user)
OrganizationKYC.objects.get(user=user)
```

---

## 🎯 Testing Commands

```python
# Django shell
python manage.py shell

# Get user
from users.models import User
user = User.objects.get(username='testuser')

# Check KYC
print(user.is_kyc_verified)
print(user.get_kyc_status())

# Manually verify (testing only)
user.is_kyc_verified = True
user.save()

# Check today's applications
print(user.get_daily_application_count())
print(user.can_apply_today())
```

---

## 📁 File Upload Paths

```
media/kyc/
├── individual/
│   ├── citizenship/
│   ├── passport/
│   ├── license/
│   ├── photos/
│   ├── address/
│   └── signatures/
└── organization/
    ├── registration/
    ├── pan/
    ├── moa/
    ├── partnership/
    ├── resolution/
    ├── address/
    ├── signatory/
    └── stamps/
```

---

## 🔐 Security Checklist

- ✅ Login required for all KYC operations
- ✅ Users can only access own KYC
- ✅ Admin requires `is_staff=True`
- ✅ CSRF protection enabled
- ✅ File type validation
- ✅ File size limits (5MB)
- ✅ Audit trail for admin actions

---

## 📞 Common Admin Tasks

### View Pending KYCs
1. Go to `/users/cms/`
2. Select "KYC Records"
3. Filter: Status = "SUBMITTED"

### Verify a KYC
1. Click on KYC record
2. Review all details
3. Click "Verify" button
4. Confirm action

### Reject a KYC
1. Click on KYC record
2. Enter rejection reason
3. Click "Reject" button
4. Confirm action

### Search for User
1. Go to `/users/cms/`
2. Select "Users" or "KYC Records"
3. Enter username/email in search
4. Click "Apply Filters"

---

## 🎓 Best Practices

### For Users:
- ✅ Use clear, high-quality images
- ✅ Ensure all text is readable
- ✅ Fill all required fields
- ✅ Double-check information before submitting
- ✅ Keep documents under 5MB

### For Admins:
- ✅ Review all documents thoroughly
- ✅ Verify information matches across documents
- ✅ Provide specific rejection reasons
- ✅ Be consistent in verification standards
- ✅ Respond to submissions promptly

---

## 📈 Metrics to Monitor

```python
# Total KYCs
IndividualKYC.objects.count()
OrganizationKYC.objects.count()

# By status
IndividualKYC.objects.filter(status='VERIFIED').count()
IndividualKYC.objects.filter(status='SUBMITTED').count()
IndividualKYC.objects.filter(status='REJECTED').count()

# Verified users
User.objects.filter(is_kyc_verified=True).count()

# Pending review
pending = (IndividualKYC.objects.filter(status='SUBMITTED').count() + 
           OrganizationKYC.objects.filter(status='SUBMITTED').count())
```

---

## 🚀 Quick Start

1. **User**: `/users/kyc/` → Fill 3 steps → Submit
2. **Admin**: `/users/cms/` → KYC Records → Review → Verify/Reject
3. **Result**: User gets full access immediately

---

## 💡 Tips

- Save progress after each step
- Upload clear, well-lit photos
- Use PDF for multi-page documents
- Check email format before submitting
- Read rejection reasons carefully
- Resubmit after fixing issues

---

**Need Help?** Check the full documentation in `KYC_SYSTEM_README.md`
