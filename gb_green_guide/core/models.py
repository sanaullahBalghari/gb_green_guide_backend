# core/models.py

from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities')
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="uploads/cities/", null=True, blank=True);
    highlights = models.TextField(
        help_text="Comma-separated highlights (e.g., Snowy Mountains, Rich Culture)",
        blank=True,
        null=True
    )
    altitude = models.CharField(max_length=100, blank=True, null=True)
    best_time_to_visit = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null= True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    def get_highlights_list(self):
        """Return highlights as list for use in templates or APIs"""
        if self.highlights:
            return [h.strip() for h in self.highlights.split(',')]
        return []

    def __str__(self):
        return f"{self.name} ({self.region.name})"


# ✅ Event model (linked to City)
class Event(models.Model):
    EVENT_TYPES = [
        ("cultural_festival", "Cultural Festival"),
        ("natural_festival", "Natural Festival"),
        ("adventure_festival", "Adventure Festival"),
        ("sports_festival", "Sports Festival"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='uploads/events/',null=True, blank=True)
    date = models.DateField()
    location = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=EVENT_TYPES)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='events')
    event_calendar = models.FileField(upload_to='event_calendars/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class TouristPlace(models.Model):
    city = models.ForeignKey(City,  on_delete=models.CASCADE, related_name='tourist_places', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='uploads/toursitplaces/', null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    location_inside_city = models.CharField(max_length=255, null=True, blank=True)
    distance_from_main_city = models.CharField(max_length=50, null=True, blank=True)
    map_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name if self.name else "Unnamed Tourist Place"


class TouristPlaceImage(models.Model):
    tourist_place = models.ForeignKey(
        TouristPlace,
        on_delete=models.CASCADE,
        related_name="extra_images",   # access via tourist_place.extra_images.all()
        null=True,
        blank=True
    )
    image = models.ImageField(
        upload_to="uploads/touristplaces/extra/",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        if self.tourist_place and self.tourist_place.name:
            return f"Image of {self.tourist_place.name}"
        return "Tourist Place Image"
