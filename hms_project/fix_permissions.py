"""
Complete permission fix - handles both class and decorator permissions
"""

import os
import re

view_files = [
    'admin_app/views.py',
    'receptionist_app/views.py',
    'doctor_app/views.py',
    'pharmacist_app/views.py',
    'labTech_app/views.py',
]

def fix_permissions(filepath):
    """Remove/comment all permission restrictions"""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        # Skip decorator permissions
        if '@permission_classes' in line:
            modified_lines.append(f'    # {line.strip()}  # COMMENTED FOR TESTING\n')
            skip_next = True
            continue
        
        # Skip the line after decorator if it contains permissions
        if skip_next and 'permission' in line.lower():
            modified_lines.append(f'    # {line.strip()}  # COMMENTED FOR TESTING\n')
            skip_next = False
            continue
        
        skip_next = False
        
        # Comment out class-level permission_classes
        if 'permission_classes' in line and '=' in line:
            # Find indentation
            indent = len(line) - len(line.lstrip())
            modified_lines.append(' ' * indent + f'# {line.strip()}  # COMMENTED FOR TESTING\n')
        else:
            modified_lines.append(line)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)
    
    print(f"✅ Fixed: {filepath}")

if __name__ == "__main__":
    print("🔧 Removing ALL permission restrictions for testing...\n")
    
    for filepath in view_files:
        fix_permissions(filepath)
    
    print("\n✅ Done! All permissions removed.")
    print("⚠️  RESTART Django server with: python manage.py runserver")
    print("⚠️  Remember to restore permissions after testing!")
