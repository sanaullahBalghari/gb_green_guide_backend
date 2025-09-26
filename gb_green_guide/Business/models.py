from django.db import models
from django.conf import settings
from core.models import City   # assuming City model is inside 'core' app, adjust import as per your project

class Restaurant(models.Model):
    RESTAURANT_TYPES = [
        ("restaurant", "Restaurant"),
        ("hotel", "Hotel & Guest House"),
        ("local_traditional", "Local & Traditional"),
        ("cafe", "Cafe"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="restaurants",
        blank=True, 
        null=True
    )
    city = models.ForeignKey(
        City, 
        on_delete=models.CASCADE, 
        related_name="restaurants",
        blank=True, 
        null=True
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    location_inside_city = models.CharField(max_length=255, blank=True, null=True)
    restaurant_type = models.CharField(max_length=50, choices=RESTAURANT_TYPES, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    room_available = models.BooleanField(default=False)

    contacts_and_hours = models.JSONField(blank=True, null=True)
    amenities = models.JSONField(blank=True, null=True)

    get_direction = models.URLField(blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)

    image = models.ImageField(upload_to="uploads/restaurants/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return str(self.name) if self.name else f"Restaurant #{self.id}"
    
    def save(self, *args, **kwargs):
        # Convert comma separated string to list before saving
        if isinstance(self.contacts_and_hours, str):
            self.contacts_and_hours = [item.strip() for item in self.contacts_and_hours.split(",") if item.strip()]
        if isinstance(self.amenities, str):
            self.amenities = [item.strip() for item in self.amenities.split(",") if item.strip()]
        super().save(*args, **kwargs)


    # ✅ WhatsApp link conversion method
    def whatsapp_link(self):
        if self.whatsapp_number:
            return f"https://wa.me/{self.whatsapp_number}"
        return None
    
