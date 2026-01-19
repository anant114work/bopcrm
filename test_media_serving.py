#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from leads.project_image_models import ProjectImage
from django.conf import settings

def test_media_serving():
    """Test media file serving configuration"""
    
    print("=== Media Configuration Test ===")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"DEBUG: {settings.DEBUG}")
    
    # Check if media directory exists
    media_exists = os.path.exists(settings.MEDIA_ROOT)
    print(f"Media directory exists: {media_exists}")
    
    if media_exists:
        project_images_dir = os.path.join(settings.MEDIA_ROOT, 'project_images')
        project_images_exists = os.path.exists(project_images_dir)
        print(f"Project images directory exists: {project_images_exists}")
        
        if project_images_exists:
            images = os.listdir(project_images_dir)
            print(f"Images found: {len(images)}")
            for img in images[:3]:  # Show first 3
                print(f"  - {img}")
    
    # Check database records
    print("\n=== Database Records ===")
    project_images = ProjectImage.objects.all()
    print(f"ProjectImage records: {project_images.count()}")
    
    for img in project_images[:3]:  # Show first 3
        print(f"  - {img.project.name}: {img.image.name}")
        print(f"    URL: {img.image.url}")
        file_path = os.path.join(settings.MEDIA_ROOT, img.image.name)
        file_exists = os.path.exists(file_path)
        print(f"    File exists: {file_exists}")
        print()
    
    print("=== Test Complete ===")
    print("If images still don't show, restart the Django server.")

if __name__ == '__main__':
    test_media_serving()