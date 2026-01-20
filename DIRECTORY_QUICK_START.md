# Organization Directory - Quick Start Guide

## 🚀 Quick Start

### Access the Page
```
URL: http://127.0.0.1:8000/organization/directory/
```

---

## 📋 Features Overview

### 1. **Search Organizations**
- Type organization name or industry in the search box
- Click "Search" button or press Enter
- Results update automatically

### 2. **Filter by Industry**
Select from dropdown:
- Information Technology
- Banking & Finance
- Healthcare
- Education
- Construction
- Retail
- Media & Entertainment
- And more...

### 3. **Filter by Location**
Select from dropdown:
- Kathmandu
- Lalitpur
- Pokhara
- Bhaktapur
- Biratnagar

### 4. **Follow Organizations**
- Click "Follow" button on any organization card
- Must be logged in as a job seeker
- Follower count updates in real-time
- Get notifications for new jobs

### 5. **View Organization Profile**
- Click "View Profile" button
- See complete organization details
- View all available jobs
- See company information

---

## 🎨 Visual Components

### Hero Section
```
┌─────────────────────────────────────────┐
│   Discover Top Organizations            │
│   Connect with leading companies...     │
│                                          │
│  [10+ Orgs]  [500+ Jobs]  [10K+ Seekers]│
└─────────────────────────────────────────┘
```

### Search & Filters
```
┌──────────────────────────────────────────┐
│ 🔍 [Search Box] [Industry▾] [Location▾] │
│                                [Search]  │
│                                          │
│ Active Filters: [IT ×] [Kathmandu ×]    │
└──────────────────────────────────────────┘
```

### Organization Card
```
┌───────────────────────────┐
│   ╔═══════════════╗       │
│   ║  [Logo/Icon]  ║ ✓     │
│   ╚═══════════════╝       │
│                           │
│   TechCorp Solutions      │
│   [IT] [Kathmandu]        │
│                           │
│   Leading IT solutions... │
│                           │
│   👥 150  💼 25  ⭐ 4.5  │
│                           │
│   [Following] [View]      │
└───────────────────────────┘
```

---

## 🔧 For Administrators

### Adding Sample Organizations
Run this command in the terminal:
```bash
cd "c:\Users\LENOVO\Desktop\sohansandhya prj\Payo"
python add_organizations_standalone.py
```

This will add 15 sample organizations across different industries.

### Default Credentials
All sample organizations:
- **Password**: `password123`
- **Usernames**: techcorp, financeplus, healthcarepro, etc.

---

## 💡 Tips & Tricks

### For Job Seekers

1. **Follow Strategic Organizations**
   - Follow companies in your industry
   - Get priority notifications for new jobs
   - Build your professional network

2. **Use Filters Effectively**
   - Combine search with industry filter
   - Filter by preferred location
   - Clear filters to explore all options

3. **Check Verified Organizations**
   - Look for the green checkmark ✓
   - These are KYC-verified companies
   - More reliable job postings

### For Developers

1. **Customize Colors**
   Edit CSS variables at the top of the style section:
   ```css
   :root {
       --primary-color: #4F46E5;  /* Change this */
       --success-color: #10B981;  /* And this */
   }
   ```

2. **Add More Statistics**
   In the organization card, add more stat boxes:
   ```html
   <div class="stat-box">
       <i class="fas fa-icon stat-icon"></i>
       <div class="stat-info">
           <span class="stat-value">Value</span>
           <span class="stat-label">Label</span>
       </div>
   </div>
   ```

3. **Modify Grid Layout**
   Change the number of columns:
   ```css
   .organizations-grid {
       grid-template-columns: repeat(4, 1fr); /* 4 columns */
   }
   ```

---

## 🐛 Troubleshooting

### Problem: Organizations Not Showing
**Solution**: 
- Check if sample organizations were added
- Run: `python add_organizations_standalone.py`
- Verify database connection

### Problem: Follow Button Not Working
**Solution**:
- Check if user is logged in
- Verify user type is 'APP' (applicant)
- Check browser console for errors
- Ensure CSRF token is present

### Problem: Filters Not Working
**Solution**:
- Check if form is submitting
- Verify URL parameters
- Clear browser cache
- Check Django view logic

### Problem: Page Looks Broken
**Solution**:
- Hard refresh (Ctrl + Shift + R)
- Clear browser cache
- Check if base2.html exists
- Verify Bootstrap is loaded

---

## 📱 Mobile Usage

### Portrait Mode
- Single column layout
- Full-width cards
- Stacked filters
- Touch-friendly buttons

### Landscape Mode
- Two-column layout
- Optimized spacing
- Horizontal scrolling for filters

---

## 🔐 Security Features

1. **CSRF Protection**
   - All POST requests include CSRF token
   - Prevents cross-site attacks

2. **Authentication Required**
   - Follow/unfollow requires login
   - Organization access restricted

3. **User Type Validation**
   - Organizations cannot access directory
   - Only applicants can follow

---

## 📊 Statistics Displayed

### Organization Level
- **Followers**: Total users following
- **Jobs**: Active job postings
- **Rating**: Organization rating (out of 5)

### Directory Level
- **Total Organizations**: All registered
- **Active Jobs**: Sum of all jobs
- **Job Seekers**: Total applicants

---

## 🎯 User Journey

### For New Visitors
1. Land on directory page
2. Browse organizations
3. Click "Follow" → Redirected to login
4. After login → Can follow organizations

### For Logged-In Users
1. Land on directory page
2. Search/filter organizations
3. Click "Follow" → Instant follow
4. View profile → See jobs
5. Apply to jobs

---

## 🔄 Real-Time Updates

### What Updates Automatically?
- ✅ Follower count after follow/unfollow
- ✅ Button state (Follow ↔ Following)
- ✅ Toast notifications
- ✅ Search results on submit

### What Requires Page Refresh?
- ❌ New organizations added
- ❌ Job count changes
- ❌ Rating updates

---

## 🎨 Customization Options

### Change Primary Color
```css
--primary-color: #your-color-here;
```

### Adjust Card Size
```css
.org-card-modern {
    /* Modify padding, width, etc. */
}
```

### Change Grid Columns
```css
.organizations-grid {
    grid-template-columns: repeat(5, 1fr); /* 5 columns */
}
```

### Modify Hero Gradient
```css
.organizations-directory-page {
    background: linear-gradient(135deg, #color1 0%, #color2 100%);
}
```

---

## 📞 Support

### Common Questions

**Q: Can organizations follow other organizations?**  
A: No, only job seekers can follow organizations.

**Q: How many organizations can I follow?**  
A: Unlimited!

**Q: Will I get notifications for new jobs?**  
A: Yes, from organizations you follow.

**Q: Can I unfollow later?**  
A: Yes, click the "Following" button to unfollow.

---

## 🚀 Performance Tips

1. **Use Filters**: Reduce page load with specific filters
2. **Pagination**: Browse one page at a time
3. **Clear Cache**: If page loads slowly
4. **Update Browser**: Use latest version

---

## 📝 Keyboard Shortcuts

- **Tab**: Navigate through filters
- **Enter**: Submit search
- **Escape**: Close modals
- **Space**: Activate buttons

---

## ✨ Best Practices

1. **Follow Relevant Organizations**
   - Don't spam follow all
   - Choose your industry
   - Target your location

2. **Use Search Wisely**
   - Be specific
   - Try different keywords
   - Combine with filters

3. **Check Profiles**
   - View before following
   - Read company info
   - Check job listings

---

**Version**: 2.0  
**Last Updated**: January 2026  
**Compatibility**: All modern browsers
