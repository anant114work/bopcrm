# Global CSS Quick Reference Guide

## 🎨 Common Classes

### Buttons
```html
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-success">Success Button</button>
<button class="btn btn-danger">Danger Button</button>
<button class="btn btn-warning">Warning Button</button>
<button class="btn btn-secondary">Secondary Button</button>
<button class="btn btn-outline">Outline Button</button>

<!-- Sizes -->
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Normal</button>
<button class="btn btn-primary btn-lg">Large</button>
```

### Cards
```html
<div class="card">
    <div class="card-header">Card Title</div>
    <div class="card-content">
        Card content goes here
    </div>
</div>
```

### Stats Cards
```html
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-label">Total Leads</div>
        <div class="stat-value">1,234</div>
        <div class="stat-change positive">+12%</div>
    </div>
</div>
```

### Forms
```html
<div class="form-group">
    <label class="form-label">Field Label</label>
    <input type="text" class="form-control" placeholder="Enter value">
</div>

<div class="form-group">
    <label class="form-label">Select Option</label>
    <select class="form-control">
        <option>Option 1</option>
        <option>Option 2</option>
    </select>
</div>

<div class="form-group">
    <label class="form-label">Message</label>
    <textarea class="form-control"></textarea>
</div>
```

### Tables
```html
<div class="table-container">
    <table class="table">
        <thead>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Data 1</td>
                <td>Data 2</td>
            </tr>
        </tbody>
    </table>
</div>
```

### Badges
```html
<span class="badge badge-success">Success</span>
<span class="badge badge-danger">Danger</span>
<span class="badge badge-warning">Warning</span>
<span class="badge badge-info">Info</span>
<span class="badge badge-primary">Primary</span>
```

### Alerts
```html
<div class="alert alert-success">Success message</div>
<div class="alert alert-danger">Error message</div>
<div class="alert alert-warning">Warning message</div>
<div class="alert alert-info">Info message</div>
```

### Layout Utilities
```html
<!-- Flexbox -->
<div class="d-flex">Flex container</div>
<div class="d-flex align-items-center">Centered items</div>
<div class="d-flex justify-content-between">Space between</div>

<!-- Gaps -->
<div class="d-flex gap-2">Small gap</div>
<div class="d-flex gap-3">Medium gap</div>
```

### Spacing Utilities
```html
<!-- Margins -->
<div class="mt-2">Margin top small</div>
<div class="mt-3">Margin top medium</div>
<div class="mb-2">Margin bottom small</div>
<div class="mb-3">Margin bottom medium</div>

<!-- Text -->
<div class="text-center">Centered text</div>
<div class="text-muted">Muted text</div>
```

### Loading Spinner
```html
<div class="spinner"></div>
```

### Pagination
```html
<div class="pagination">
    <a href="#">Previous</a>
    <span class="active">1</span>
    <a href="#">2</a>
    <a href="#">3</a>
    <a href="#">Next</a>
</div>
```

## 🎯 CSS Variables

Use these in your custom styles:

```css
var(--primary)        /* #3498db */
var(--primary-dark)   /* #2980b9 */
var(--secondary)      /* #2c3e50 */
var(--success)        /* #27ae60 */
var(--danger)         /* #e74c3c */
var(--warning)        /* #f39c12 */
var(--info)           /* #16a085 */
var(--gray)           /* #95a5a6 */
var(--shadow)         /* 0 2px 8px rgba(0,0,0,0.1) */
var(--shadow-lg)      /* 0 4px 16px rgba(0,0,0,0.15) */
var(--radius)         /* 8px */
var(--transition)     /* all 0.3s ease */
```

## 📝 Example Page Template

```django
{% extends 'leads/base_unified.html' %}

{% block title %}My Page - Meta Leads CRM{% endblock %}
{% block page_title %}My Page Title{% endblock %}

{% block content %}
<div class="card">
    <div class="card-header">
        <h2>Section Title</h2>
    </div>
    <div class="card-content">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Metric 1</div>
                <div class="stat-value">100</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Metric 2</div>
                <div class="stat-value">200</div>
            </div>
        </div>
        
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Item 1</td>
                        <td><span class="badge badge-success">Active</span></td>
                        <td>
                            <button class="btn btn-primary btn-sm">Edit</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
```

## 🚀 Tips

1. **Always extend base_unified.html** for consistent layout
2. **Use utility classes** instead of inline styles
3. **Combine classes** for complex layouts
4. **Use CSS variables** for custom colors
5. **Test responsive** design on mobile

## 📱 Responsive Breakpoints

- **Desktop**: > 768px (full sidebar)
- **Mobile**: ≤ 768px (collapsible sidebar)

---

**Quick Start**: Just extend `base_unified.html` and use the classes above!
