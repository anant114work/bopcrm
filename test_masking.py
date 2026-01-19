#!/usr/bin/env python3
"""
Test script to demonstrate number masking functionality
"""

import re

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

def test_masking():
    """Test the masking functionality with various phone number formats"""
    test_numbers = [
        "9876543210",           # 10 digit phone
        "+91 9876543210",       # With country code
        "91-9876-543210",       # With dashes
        "98765 43210",          # With space
        "123456",               # 6 digit number
        "1234",                 # 4 digit number
        "123",                  # 3 digit number
        "7710608142",           # Real example
        "1919229005",           # Another real example
        "8619464946",           # Another real example
    ]
    
    print("Number Masking Test Results:")
    print("=" * 50)
    
    for number in test_numbers:
        masked = mask_number(number)
        print(f"Original: {number:15} -> Masked: {masked}")
    
    print("\nAdmin vs Regular User View:")
    print("=" * 50)
    print("Regular User sees: 98xxxx10")
    print("Admin clicks to see: 9876543210")
    print("Admin clicks again: 98xxxx10")

if __name__ == "__main__":
    test_masking()