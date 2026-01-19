#!/usr/bin/env python3
"""
Analyze call patterns to identify agent vs customer numbers
"""
import os
import django
from collections import Counter

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

def analyze_call_patterns():
    """Analyze call patterns to identify frequent numbers"""
    try:
        from tata_integration.models import TataCall
        
        # Get all calls
        calls = TataCall.objects.all()
        
        # Count frequency of each number
        number_frequency = Counter()
        agent_numbers = Counter()
        
        for call in calls:
            if call.customer_number:
                number_frequency[call.customer_number] += 1
                if call.agent_name and call.agent_name != 'Unknown':
                    agent_numbers[call.customer_number] = call.agent_name
        
        print("Call Pattern Analysis")
        print("=" * 50)
        print(f"Total calls analyzed: {calls.count()}")
        print(f"Unique numbers: {len(number_frequency)}")
        
        print("\nMost Frequent Numbers (Likely Agent Numbers):")
        for number, count in number_frequency.most_common(10):
            agent_name = agent_numbers.get(number, 'Unknown')
            masked = number[:2] + 'xxxx' + number[-2:] if len(number) >= 6 else 'xxxx'
            print(f"  {masked} - {count} calls - Agent: {agent_name}")
        
        print(f"\nNumbers with 10+ calls: {sum(1 for count in number_frequency.values() if count >= 10)}")
        print(f"Numbers with 5+ calls: {sum(1 for count in number_frequency.values() if count >= 5)}")
        print(f"Single call numbers: {sum(1 for count in number_frequency.values() if count == 1)}")
        
        return number_frequency
        
    except Exception as e:
        print(f"Error analyzing patterns: {e}")
        return {}

if __name__ == "__main__":
    analyze_call_patterns()