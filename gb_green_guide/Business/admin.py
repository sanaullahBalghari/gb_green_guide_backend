from django import forms
from django.contrib import admin
from .models import Restaurant


class RestaurantAdminForm(forms.ModelForm):
    contacts_and_hours = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Enter values separated by commas"})
    )
    amenities = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Enter values separated by commas"})
    )

    class Meta:
        model = Restaurant
        fields = "__all__"

    def clean_contacts_and_hours(self):
        data = self.cleaned_data.get("contacts_and_hours")
        if data:
            return [item.strip() for item in data.split(",") if item.strip()]
        return []

    def clean_amenities(self):
        data = self.cleaned_data.get("amenities")
        if data:
            return [item.strip() for item in data.split(",") if item.strip()]
        return []


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    form = RestaurantAdminForm   # <-- yeh line add ki hai

    list_display = (
        "name",
        "restaurant_type",
        "city",
        "owner",
        "is_active",
        "room_available",
        "created_at",
    )
    list_filter = (
        "restaurant_type",
        "city",
        "is_active",
        "room_available",
        "created_at",
    )
    search_fields = ("name", "owner__username", "city__name", "whatsapp_number")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "city", "owner", "restaurant_type", "description", "image"),
        }),
        ("Contact & Location", {
            "fields": ("location_inside_city", "contacts_and_hours", "get_direction", "whatsapp_number"),
        }),
        ("Amenities & Availability", {
            "fields": ("room_available", "amenities"),
        }),
        ("Status & Metadata", {
            "fields": ("is_active", "created_at", "updated_at"),
        }),
    )
