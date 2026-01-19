#!/usr/bin/env python3
"""
Test script to verify phone number formatting logic
"""

def format_phone_number(phone_number):
    """Format phone number for Call Karo AI"""
    original_phone = phone_number
    phone = phone_number.strip()
    
    print(f"\nPHONE FORMATTING DEBUG:")
    print(f"Original: '{original_phone}'")
    print(f"After strip: '{phone}'")
    
    # Extract only digits
    digits_only = ''.join(filter(str.isdigit, phone))
    print(f"Digits only: '{digits_only}'")
    
    # Take last 10 digits (right to left)
    if len(digits_only) >= 10:
        phone = f"+91{digits_only[-10:]}"
        print(f"Final formatted: '{phone}'")
        return phone, True
    else:
        print(f"INVALID format - Not enough digits: {len(digits_only)}")
        return phone, False

# Test cases
test_numbers = [
    "7011628053",           # Normal 10-digit
    "+917011628053",        # Already formatted correctly
    "917011628053",         # With 91 prefix
    "+1917011628053",       # Wrong format (extra 1)
    "+16395068729",         # US number - should take last 10 digits
    "91 7011628053",        # With space
    " +917011628053 ",      # With spaces
    "8808604159",           # Another normal number
    "+918808604159",        # Already formatted
    "918808604159",         # With 91 prefix
    "123456789",            # Invalid (9 digits)
    "12345678901",          # Invalid (11 digits)
    "abcd123456",           # Invalid (non-numeric)
]

print("=" * 60)
print("PHONE NUMBER FORMATTING TEST")
print("=" * 60)

for test_number in test_numbers:
    formatted, is_valid = format_phone_number(test_number)
    status = "VALID" if is_valid else "INVALID"
    print(f"{status} - Result: {formatted}")
    print("-" * 40)