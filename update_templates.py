#!/usr/bin/env python3

import os
import re

# Path to templates directory
templates_dir = r"d:\AI-proto\CRM\drip\leads\templates\leads"

# Files to update (excluding the ones we already updated)
updated_files = [
    'base_unified.html',
    'base_sidebar.html', 
    'my_leads.html',
    'projects_list.html',
    'whatsapp.html',
    'team_members.html',
    'list.html'
]

def update_template_file(filepath):
    """Update a template file to use unified base and remove inline CSS"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already using base_unified or if it's a base file itself
        if 'base_unified.html' in content or 'base.html' in os.path.basename(filepath):
            return False
            
        # Replace extends statements
        content = re.sub(
            r"{% extends ['\"]leads/base_sidebar\.html['\"] %}",
            "{% extends 'leads/base_unified.html' %}",
            content
        )
        content = re.sub(
            r"{% extends ['\"]leads/base_crm\.html['\"] %}",
            "{% extends 'leads/base_unified.html' %}",
            content
        )
        content = re.sub(
            r"{% extends ['\"]leads/base\.html['\"] %}",
            "{% extends 'leads/base_unified.html' %}",
            content
        )
        
        # Remove extra_css blocks with inline styles
        content = re.sub(
            r"{% block extra_css %}.*?{% endblock %}",
            "",
            content,
            flags=re.DOTALL
        )
        
        # Replace common inline styles with CSS classes
        style_replacements = [
            (r'style="[^"]*margin-bottom:\s*0[^"]*"', 'class="mb-0"'),
            (r'style="[^"]*text-align:\s*center[^"]*"', 'class="text-center"'),
            (r'style="[^"]*color:\s*#64748b[^"]*"', 'class="text-muted"'),
            (r'style="[^"]*font-size:\s*12px[^"]*"', 'class="small"'),
            (r'style="[^"]*font-size:\s*14px[^"]*"', 'class="small"'),
            (r'style="[^"]*display:\s*flex[^"]*"', 'class="d-flex"'),
            (r'style="[^"]*gap:\s*[^"]*"', 'class="gap-2"'),
        ]
        
        for pattern, replacement in style_replacements:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # Write back the updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
        return False

def main():
    """Update all HTML template files"""
    if not os.path.exists(templates_dir):
        print(f"Templates directory not found: {templates_dir}")
        return
    
    updated_count = 0
    total_count = 0
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html') and filename not in updated_files:
            filepath = os.path.join(templates_dir, filename)
            total_count += 1
            
            if update_template_file(filepath):
                updated_count += 1
                print(f"Updated: {filename}")
            else:
                print(f"Skipped: {filename}")
    
    print(f"\nSummary: Updated {updated_count} out of {total_count} template files")

if __name__ == "__main__":
    main()