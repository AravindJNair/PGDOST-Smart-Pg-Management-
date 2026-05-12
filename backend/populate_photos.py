import os
import django
from urllib.request import urlopen
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pgdost_backend.settings')
django.setup()

from properties.models import Property, PropertyImage

IMAGE_URLS = [
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80",  # bedroom
    "https://images.unsplash.com/photo-1502672260266-1c1e5240980c?w=800&q=80",  # living room
    "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&q=80",  # office/desk
    "https://images.unsplash.com/photo-1554995207-c18c203602cb?w=800&q=80",  # interior
    "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?w=800&q=80",  # kitchen
    "https://images.unsplash.com/photo-1540518614846-7eded433c457?w=800&q=80",  # bedroom 2
]

def populate():
    properties = Property.objects.all()
    if not properties.exists():
        print("No properties found to add images to.")
        return

    for prop in properties:
        print(f"Adding photos to {prop.name}...")
        # Clear existing images
        prop.images.all().delete()
        
        # Add 3 random images for each property
        for i in range(3):
            url = IMAGE_URLS[(prop.id + i) % len(IMAGE_URLS)]
            print(f"  Downloading image {i+1}...")
            response = urlopen(url)
            
            image_name = f"prop_{prop.id}_photo_{i+1}.jpg"
            img_obj = PropertyImage(
                property=prop,
                caption=f"Photo {i+1} for {prop.name}",
                is_primary=(i == 0) # Make the first one primary
            )
            img_obj.image.save(image_name, ContentFile(response.read()), save=True)
            
    print("Done! Photos added successfully.")

if __name__ == '__main__':
    populate()
