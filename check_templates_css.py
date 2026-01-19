import os
import re

def check_and_update_templates():
    """Check all HTML templates and ensure they have global CSS included"""
    
    templates_dir = 'leads/templates/leads'
    updated_files = []
    already_good = []
    
    # Pattern to check if template extends base or has static CSS
    extends_base_pattern = r"{%\s*extends\s+['\"]leads/(base_unified|base)\.html['\"]\s*%}"
    has_static_load = r"{%\s*load\s+static\s*%}"
    has_global_css = r"{% static 'css/global\.css' %}"
    
    for filename in os.listdir(templates_dir):
        if not filename.endswith('.html'):
            continue
            
        filepath = os.path.join(templates_dir, filename)
        
        # Skip base templates
        if filename in ['base.html', 'base_unified.html', 'base_sidebar.html']:
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it extends base_unified or base
        if re.search(extends_base_pattern, content):
            already_good.append(filename)
            continue
        
        # Check if it already has global CSS
        if re.search(has_global_css, content):
            already_good.append(filename)
            continue
        
        # If it's a standalone template without extending base, add global CSS
        if not re.search(extends_base_pattern, content):
            # Check if it has <head> tag
            if '<head>' in content:
                # Check if it already has {% load static %}
                if not re.search(has_static_load, content):
                    # Add {% load static %} after <head>
                    content = content.replace('<head>', '<head>\n    {% load static %}')
                
                # Add global CSS link after <head> or after existing CSS links
                if '<link' in content:
                    # Find the last <link> tag and add after it
                    last_link_pos = content.rfind('</head>')
                    if last_link_pos > 0:
                        insert_pos = content.rfind('<link', 0, last_link_pos)
                        if insert_pos > 0:
                            # Find end of that link tag
                            insert_pos = content.find('>', insert_pos) + 1
                            content = content[:insert_pos] + '\n    <link rel="stylesheet" href="{% static \'css/global.css\' %}">' + content[insert_pos:]
                else:
                    # Add before </head>
                    content = content.replace('</head>', '    <link rel="stylesheet" href="{% static \'css/global.css\' %}">\n</head>')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                updated_files.append(filename)
    
    print("=" * 60)
    print("TEMPLATE CSS CHECK RESULTS")
    print("=" * 60)
    print(f"\n[OK] Already using global CSS ({len(already_good)} files):")
    for f in already_good[:10]:  # Show first 10
        print(f"   - {f}")
    if len(already_good) > 10:
        print(f"   ... and {len(already_good) - 10} more")
    
    print(f"\n[UPDATED] Updated to include global CSS ({len(updated_files)} files):")
    for f in updated_files:
        print(f"   - {f}")
    
    if not updated_files:
        print("\n[SUCCESS] All templates are already configured correctly!")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_and_update_templates()
