from django import template
import re

register = template.Library()

@register.filter
def mask_number(value):
    """Mask numbers by replacing middle digits with xxxx"""
    if not value:
        return value
    
    # Convert to string and remove any spaces or special characters for processing
    clean_value = str(value).strip()
    
    # Check if it contains digits
    if re.search(r'\d', clean_value):
        # Extract only digits
        digits_only = re.sub(r'\D', '', clean_value)
        
        # Different masking strategies based on length
        if len(digits_only) >= 10:  # Phone numbers (10+ digits)
            masked = digits_only[:2] + 'xxxx' + digits_only[-2:]
            return masked
        elif len(digits_only) >= 6:  # Medium numbers (6-9 digits)
            masked = digits_only[:2] + 'xxxx' + digits_only[-2:]
            return masked
        elif len(digits_only) >= 4:  # Short numbers (4-5 digits)
            masked = digits_only[:1] + 'xxxx' + digits_only[-1:]
            return masked
        else:  # Very short numbers (1-3 digits)
            return 'xxxx'
    
    return clean_value

@register.filter
def is_customer_number(call_record):
    """Check if this is actually a customer call based on API data"""
    # In the API data, caller_id_num is the actual customer
    # The confusion comes from displaying caller_id_num in Customer column
    return True  # caller_id_num is always customer in inbound calls

@register.filter
def get_actual_customer(call_record):
    """Get the actual customer number from call record"""
    # caller_id_num is the customer who called in
    return getattr(call_record, 'customer_number', '') or getattr(call_record, 'caller_id_num', '')

@register.simple_tag(takes_context=True)
def maskable_number(context, value, field_name):
    """Create a maskable number element that can be clicked to reveal"""
    if not value:
        return value
    
    request = context.get('request')
    # Check multiple admin conditions
    is_admin = False
    if request:
        # Check Django superuser
        if hasattr(request, 'user') and request.user and request.user.is_superuser:
            is_admin = True
        # Check session admin flag
        elif hasattr(request, 'session') and request.session.get('is_admin'):
            is_admin = True
    
    masked_value = mask_number(value)
    
    if is_admin:
        from django.utils.safestring import mark_safe
        return mark_safe(f'''<span class="maskable-number" 
                        data-masked="{masked_value}" 
                        data-original="{value}" 
                        data-field="{field_name}"
                        onclick="toggleMask(this)"
                        style="cursor: pointer; user-select: none;">
                        {masked_value}
                   </span>''')
    else:
        return masked_value

@register.filter
def format_call_direction(direction, customer_num, agent_num):
    """Format call direction with proper customer/agent labels"""
    if direction == 'inbound':
        return f"Customer {customer_num} → Agent {agent_num or 'System'}"
    else:
        return f"Agent {agent_num or 'System'} → Customer {customer_num}"