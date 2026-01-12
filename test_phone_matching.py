#!/usr/bin/env python3
"""
Test script for phone number matching logic
"""
import re

def normalize_phone_number(phone):
    """Normalize phone number by removing all non-digit characters"""
    if not phone:
        return ""
    # Handle float format from Excel (e.g., 9876543210.0)
    phone_str = str(phone)
    if '.' in phone_str:
        phone_str = phone_str.split('.')[0]  # Remove decimal part
    return re.sub(r'\D', '', phone_str)

def match_phone_numbers(excel_phone, crm_phone):
    """
    Match phone numbers by comparing last 10 digits only
    """
    excel_clean = normalize_phone_number(excel_phone)
    crm_clean = normalize_phone_number(crm_phone)
    
    if not excel_clean or not crm_clean:
        return False, 0
    
    # Get last 10 digits for both numbers
    excel_last10 = excel_clean[-10:] if len(excel_clean) >= 10 else excel_clean
    crm_last10 = crm_clean[-10:] if len(crm_clean) >= 10 else crm_clean
    
    # Match only if last 10 digits are identical
    if excel_last10 == crm_last10 and len(excel_last10) >= 10:
        return True, 1  # Match found
    
    return False, 0

# Test cases
test_cases = [
    # (excel_phone, crm_phone, expected_match, expected_score)
    ("+91 9876543210", "9876543210", True, 1),  # Full match
    ("+91-9876-543-210", "919876543210", True, 1),  # Full match with country code
    ("9876543210", "+91 9876543210", True, 1),  # Full match reverse
    ("1234567890", "9876543210", False, 0),  # No match
    ("9876543210", "1234563210", False, 0),  # Different numbers
    ("98765-43210", "87654-43210", False, 0),  # Different numbers
    ("", "9876543210", False, 0),  # Empty excel phone
    ("9876543210", "", False, 0),  # Empty CRM phone
    ("123", "456", False, 0),  # Too short
    ("1234", "5678", False, 0),  # Too short
    ("9876543210.0", "9876543210", True, 1),  # Excel float format
    ("9.876543210e+09", "9876543210", False, 0),  # Scientific notation (no match)
]

def run_tests():
    print("Testing Phone Number Matching Logic")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for i, (excel_phone, crm_phone, expected_match, expected_score) in enumerate(test_cases, 1):
        is_match, score = match_phone_numbers(excel_phone, crm_phone)
        
        if is_match == expected_match and score == expected_score:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1
        
        print(f"Test {i:2d}: {status}")
        print(f"  Excel: '{excel_phone}' -> CRM: '{crm_phone}'")
        print(f"  Expected: Match={expected_match}, Score={expected_score}")
        print(f"  Got:      Match={is_match}, Score={score}")
        print()
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed!")
    else:
        print("Some tests failed!")

if __name__ == "__main__":
    run_tests()