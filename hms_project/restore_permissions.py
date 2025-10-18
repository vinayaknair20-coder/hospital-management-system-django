"""
Restore Production Permissions
Uncomments all permission classes that were disabled for testing
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

def restore_permissions(filepath):
    """Restore all commented permission classes"""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track changes
    changes_made = 0
    
    # Pattern 1: Uncomment permission_classes with "# COMMENTED FOR TESTING"
    # Matches: # permission_classes = [IsAuthenticated] # COMMENTED FOR TESTING
    pattern1 = r'#\s*(permission_classes\s*=\s*\[.*?\])\s*#\s*COMMENTED FOR TESTING'
    matches1 = re.findall(pattern1, content)
    changes_made += len(matches1)
    content = re.sub(pattern1, r'\1', content)
    
    # Pattern 2: Uncomment standalone commented permission_classes
    # Matches: # permission_classes = [IsAuthenticated]
    pattern2 = r'^\s*#\s+(permission_classes\s*=\s*\[.*?\])'
    matches2 = re.findall(pattern2, content, re.MULTILINE)
    changes_made += len(matches2)
    content = re.sub(pattern2, r'    \1', content, flags=re.MULTILINE)
    
    # Pattern 3: Uncomment @permission_classes decorators
    # Matches: # @permission_classes([AllowAny])
    pattern3 = r'#\s*(@permission_classes\([^)]+\))\s*#\s*COMMENTED FOR TESTING'
    matches3 = re.findall(pattern3, content)
    changes_made += len(matches3)
    content = re.sub(pattern3, r'\1', content)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if changes_made > 0:
        print(f"✅ Restored: {filepath} ({changes_made} permissions uncommented)")
    else:
        print(f"⚠️  No changes needed: {filepath}")
    
    return changes_made

if __name__ == "__main__":
    print("=" * 80)
    print("🔒 RESTORING PRODUCTION PERMISSIONS")
    print("=" * 80)
    print("\nThis will re-enable authentication on all endpoints.\n")
    
    total_changes = 0
    
    for filepath in view_files:
        changes = restore_permissions(filepath)
        if changes:
            total_changes += changes
    
    print("\n" + "=" * 80)
    if total_changes > 0:
        print(f"✅ SUCCESS! Restored {total_changes} permission restrictions")
        print("=" * 80)
        print("\n🔐 Authentication is now ENABLED")
        print("\n📋 Next Steps:")
        print("   1. Restart Django server: python manage.py runserver")
        print("   2. Users must login to get JWT tokens")
        print("   3. Include token in requests: Authorization: Bearer <token>")
        print("\n💡 To test authenticated endpoints:")
        print("   - POST /api/admin/staff/login/ to get tokens")
        print("   - Add header: Authorization: Bearer <access_token>")
    else:
        print("⚠️  No permissions were commented - files already in production state")
        print("=" * 80)
    print()
