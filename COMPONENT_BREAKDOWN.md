# Organization Directory - Modular Component Breakdown

## Component Architecture

The Organization Directory page is built using a modular component-based architecture. Each section is independent and reusable.

---

## 1. Hero Section Component
**Purpose**: Welcome users and display key statistics

### Structure:
```
Hero Section
├── Container
│   ├── Title
│   ├── Subtitle
│   └── Statistics Cards
│       ├── Organizations Count Card
│       ├── Active Jobs Card
│       └── Job Seekers Card
```

### Features:
- Gradient background (purple to pink)
- Animated fade-in effect
- Glass-morphism stats cards
- Responsive grid layout

### CSS Classes:
- `.hero-section`
- `.hero-title`
- `.hero-subtitle`
- `.hero-stats`
- `.stat-card`

---

## 2. Search & Filter Component
**Purpose**: Allow users to search and filter organizations

### Structure:
```
Search Filter Wrapper
├── Search Box Modern
│   ├── Form
│   │   ├── Search Input (Organization name/industry)
│   │   ├── Industry Dropdown
│   │   ├── Location Dropdown
│   │   └── Search Button
│   └── Active Filters Display
│       ├── Filter Badges
│       └── Clear All Button
```

### Features:
- Form submission with GET parameters
- Real-time filter badge display
- Individual filter removal
- Clear all filters option
- Focus states with primary color

### CSS Classes:
- `.search-filter-wrapper`
- `.search-box-modern`
- `.active-filters`
- `.filter-badge`
- `.filter-remove`

---

## 3. Organization Card Component
**Purpose**: Display individual organization information

### Structure:
```
Organization Card
├── Card Header
│   ├── Gradient Background
│   └── Logo Wrapper
│       ├── Organization Logo/Placeholder
│       └── Verified Badge (if KYC verified)
├── Card Content
│   ├── Organization Name
│   ├── Tags (Industry & Location)
│   ├── Bio/Description
│   └── Statistics
│       ├── Followers Count
│       ├── Jobs Count
│       └── Rating
└── Card Footer
    ├── Follow/Unfollow Button
    └── View Profile Button
```

### States:
1. **Default State**: Normal card display
2. **Hover State**: Elevated with enhanced shadow
3. **Loading State**: Spinner during API calls
4. **Followed State**: Green button showing "Following"
5. **Unfollowed State**: Blue button showing "Follow"

### CSS Classes:
- `.org-card-modern`
- `.org-card-header`
- `.org-header-bg`
- `.org-logo-wrapper`
- `.org-logo-modern`
- `.org-logo-placeholder-modern`
- `.verified-badge`
- `.org-card-content`
- `.org-name-modern`
- `.org-tags`
- `.tag`
- `.org-bio`
- `.org-statistics`
- `.stat-box`
- `.org-card-footer`

---

## 4. Pagination Component
**Purpose**: Navigate through multiple pages of organizations

### Structure:
```
Pagination Modern
├── First Page Link
├── Previous Page Link
├── Current Page Display
├── Next Page Link
└── Last Page Link
```

### Features:
- Icon-based navigation
- Active page highlighting
- Conditional display (only if multiple pages)
- Preserves search/filter parameters

### CSS Classes:
- `.pagination-modern`
- `.page-item-modern`
- `.page-link-modern`

---

## 5. No Results Component
**Purpose**: Display when no organizations match filters

### Structure:
```
No Results Modern
├── Icon Container
├── Heading
├── Description Message
└── View All Button (if filtered)
```

### CSS Classes:
- `.no-results-modern`
- `.no-results-icon`

---

## 6. Login Modal Component
**Purpose**: Prompt non-authenticated users to log in

### Structure:
```
Login Required Modal
├── Modal Header
│   ├── Title with Icon
│   └── Close Button
├── Modal Body
│   ├── Lock Icon
│   ├── Heading
│   └── Description
└── Modal Footer
    ├── Cancel Button
    └── Log In Button
```

### Features:
- Bootstrap modal integration
- Redirect to login with next parameter
- Centered display
- Modern styling

---

## JavaScript Functions

### 1. `getCookie(name)`
**Purpose**: Retrieve CSRF token for Django

### 2. `followOrganization(orgId)`
**Purpose**: Follow an organization
- Updates button state
- Updates follower count
- Shows toast notification
- Handles errors

### 3. `unfollowOrganization(orgId)`
**Purpose**: Unfollow an organization
- Updates button state
- Updates follower count
- Shows toast notification
- Handles errors

### 4. `handleLoginRequired()`
**Purpose**: Show login modal for guest users

### 5. `showToast(type, message)`
**Purpose**: Display toast notifications
- Auto-dismissible after 5 seconds
- Slide-in animation
- Success/Error variants

---

## CSS Design Patterns Used

### 1. **CSS Variables**
Centralized color and spacing management
```css
:root {
    --primary-color: #4F46E5;
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    /* ... more variables */
}
```

### 2. **Flexbox Layout**
Used for:
- Search form alignment
- Card footer buttons
- Statistics display
- Filter badges

### 3. **CSS Grid**
Used for:
- Organizations grid (responsive)
- Statistics section in cards

### 4. **Transitions**
Smooth hover effects:
```css
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

### 5. **Glass-morphism**
Hero section stat cards:
```css
background: rgba(255, 255, 255, 0.15);
backdrop-filter: blur(10px);
```

---

## Responsive Breakpoints

### Desktop (> 1200px)
```css
.organizations-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
}
```

### Tablet (768px - 1200px)
```css
.organizations-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}
```

### Mobile (< 768px)
```css
.organizations-grid {
    grid-template-columns: 1fr;
}
```

---

## Data Flow

### 1. Server-Side (Django)
```
View (organizations_directory)
    ↓
Query organizations from database
    ↓
Apply filters (search, industry, location)
    ↓
Annotate with follower count
    ↓
Paginate results (20 per page)
    ↓
Render template with context
```

### 2. Client-Side (JavaScript)
```
User clicks Follow button
    ↓
AJAX POST request to /organization/follow/{id}/
    ↓
Server processes request
    ↓
Response with success/error
    ↓
Update UI (button state, follower count)
    ↓
Show toast notification
```

---

## Component Dependencies

### External Libraries
1. **Bootstrap 5**: Modal, form controls, utilities
2. **Font Awesome**: Icons
3. **Google Fonts**: Inter font family

### Django Template Tags
1. `{% extends "base2.html" %}`
2. `{% load static %}`
3. `{% url %}` for URL generation
4. `{{ variable }}` for data rendering
5. `{% if %}` for conditional rendering
6. `{% for %}` for iteration

---

## Accessibility Considerations

### Semantic HTML
- `<nav>` for pagination
- `<section>` for major sections
- `<article>` for organization cards
- `<button>` for interactive elements
- `<a>` for navigation links

### ARIA Labels
- `aria-label` on pagination
- `title` attributes on buttons
- Alt text for images

### Keyboard Navigation
- Tab through filters and buttons
- Enter to submit search
- Escape to close modal

---

## Performance Optimizations

### 1. CSS
- Single compiled stylesheet
- No external CSS files
- Inline critical CSS
- Efficient selectors

### 2. JavaScript
- Minimal DOM manipulation
- Event delegation where possible
- Debounced search (potential enhancement)
- Lazy loading images (potential enhancement)

### 3. Database
- Efficient queries with `select_related`
- Annotated queries for follower count
- Pagination to limit results
- Indexed fields for search

---

## Testing Strategy

### Unit Tests (Recommended)
1. Test follow/unfollow functionality
2. Test search and filter logic
3. Test pagination
4. Test authentication checks

### Integration Tests
1. Test complete user journey
2. Test API endpoints
3. Test form submission

### UI Tests
1. Test responsive design
2. Test button states
3. Test modal display
4. Test animations

---

## Maintenance Guidelines

### Adding New Features
1. Create new component section
2. Follow existing naming conventions
3. Use CSS variables for colors
4. Maintain responsive design
5. Update documentation

### Modifying Existing Components
1. Check all breakpoints
2. Test button states
3. Verify accessibility
4. Update component diagram
5. Test cross-browser compatibility

---

**Component Count**: 6 major components  
**CSS Classes**: 50+ custom classes  
**JavaScript Functions**: 5 core functions  
**Responsive Breakpoints**: 3 levels
