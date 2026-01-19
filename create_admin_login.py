import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.models import TeamMember

# Create admin user
admin_name = "admin"
admin_phone = "8882443789"
admin_email = "admin@crm.com"

# Check if admin already exists
if TeamMember.objects.filter(phone=admin_phone).exists():
    admin = TeamMember.objects.get(phone=admin_phone)
    admin.name = admin_name
    admin.role = 'Admin'
    admin.email = admin_email
    admin.is_active = True
    admin.save()
    print(f"Admin user updated successfully!")
    print(f"Username: {admin_name}")
    print(f"Phone (Password): {admin_phone}")
    print(f"Role: Admin")
else:
    # Create new admin
    admin = TeamMember.objects.create(
        name=admin_name,
        email=admin_email,
        phone=admin_phone,
        role='Admin',
        is_active=True
    )
    print(f"Admin user created successfully!")
    print(f"Username: {admin_name}")
    print(f"Phone (Password): {admin_phone}")
    print(f"Role: Admin")

print(f"\nLogin at: /team/login/")
print(f"Username: {admin_name}")
print(f"Password: {admin_phone}")
