# Number Masking Implementation

## Overview
This implementation adds number masking functionality to the CRM system where all phone numbers are masked with "xxxx" in the middle, and only admin users can unmask them by clicking.

## Features

### 1. Automatic Number Masking
- All phone numbers are automatically masked in the format: `98xxxx10`
- Masking preserves first 2 and last 2 digits for 10+ digit numbers
- Shorter numbers use appropriate masking patterns
- Works with various phone number formats (with spaces, dashes, country codes)

### 2. Admin-Only Unmasking
- Only admin users see clickable masked numbers
- Regular users see only the masked version
- Admin detection works with both Django superusers and session-based admin flags

### 3. Click-to-Toggle Functionality
- Admins can click on masked numbers to reveal the full number
- Clicking again re-masks the number
- Visual feedback with color changes and hover effects

## Implementation Details

### Files Modified/Created

1. **Template Filter**: `leads/templatetags/lead_filters.py`
   - `mask_number()` - Core masking logic
   - `maskable_number()` - Template tag for admin-clickable elements

2. **Templates Updated**:
   - `leads/templates/leads/list.html` - Main leads list
   - `leads/templates/leads/detail.html` - Lead detail page
   - `leads/templates/leads/whatsapp_new.html` - WhatsApp interface
   - `leads/templates/leads/google_leads.html` - Google leads
   - `leads/templates/leads/meta_leads.html` - Meta leads
   - `leads/templates/leads/base_sidebar.html` - Base template with CSS

3. **Test File**: `test_masking.py` - Demonstrates masking functionality

### Usage in Templates

```html
{% load lead_filters %}

<!-- For admin-clickable masking -->
{% maskable_number lead.phone_number "phone" %}

<!-- For simple masking only -->
{{ lead.phone_number|mask_number }}
```

### JavaScript Function

```javascript
function toggleMask(element) {
    const isCurrentlyMasked = element.textContent === element.dataset.masked;
    element.textContent = isCurrentlyMasked ? element.dataset.original : element.dataset.masked;
    element.style.color = isCurrentlyMasked ? '#10b981' : '#6b7280';
}
```

## Masking Examples

| Original Number | Masked Version |
|----------------|----------------|
| 9876543210     | 98xxxx10       |
| +91 9876543210 | 91xxxx10       |
| 91-9876-543210 | 91xxxx10       |
| 123456         | 12xxxx56       |
| 1234           | 1xxxx4         |
| 123            | xxxx           |

## Security Features

1. **Admin-Only Access**: Only users with admin privileges can unmask numbers
2. **No Data Exposure**: Masked data is generated on-the-fly, original data remains secure
3. **Visual Indicators**: Hover effects show admins that numbers are clickable
4. **Session-Based**: Works with both Django auth and custom session management

## Browser Compatibility

- Modern browsers with JavaScript enabled
- CSS hover effects for better UX
- Graceful degradation for non-JS environments

## Testing

Run the test script to verify masking logic:

```bash
python test_masking.py
```

## Future Enhancements

1. **Audit Logging**: Track when admins unmask numbers
2. **Time-Limited Unmasking**: Auto re-mask after a timeout
3. **Role-Based Permissions**: Different masking levels for different roles
4. **Email Masking**: Extend to email addresses if needed
5. **Export Masking**: Ensure exports also respect masking rules

## Configuration

The masking behavior can be customized by modifying the `mask_number()` function in `lead_filters.py`:

- Change masking pattern (currently "xxxx")
- Adjust number of visible digits
- Modify length thresholds for different masking strategies

## Notes

- All phone number fields across the CRM are now masked
- The implementation is minimal and focused on the core requirement
- Admin detection works with existing authentication systems
- No database changes required - masking is template-level only