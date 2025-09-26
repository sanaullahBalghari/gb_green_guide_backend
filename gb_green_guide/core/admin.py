from django.contrib import admin
from .models import Region, City, Event, TouristPlace,TouristPlaceImage



admin.site.site_header = "GB GREEN GUIDE"


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name']  # Make "name" clickable to edit


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'region']
    list_display_links = ['name']  # Make "name" clickable to edit
    search_fields = ['name']
    list_filter = ['region']

# events 
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'type', 'date', 'location', 'created_at')
    list_filter = ('type', 'city', 'date')
    search_fields = ('title', 'description', 'location')
    ordering = ('-date',)




# ✅ Tourist Place Images Inline
class TouristPlaceImageInline(admin.TabularInline):  # or StackedInline if you prefer
    model = TouristPlaceImage
    extra = 4  # show 4 empty slots for images by default
    fields = ['image']
    verbose_name = "Additional Image"
    verbose_name_plural = "Additional Images"


# ✅ Tourist Places
@admin.register(TouristPlace)
class TouristPlaceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'city_name',
        'distance_from_main_city',
        'location_inside_city',
        'map_link',
        'created_at'
    )
    list_filter = ('city',)
    search_fields = ('name', 'city__name', 'location_inside_city')
    ordering = ('city', 'name')
    inlines = [TouristPlaceImageInline]  # 🔑 add inline images here

    def city_name(self, obj):
        return obj.city.name if obj.city else "-"
    city_name.short_description = 'City'

    def map_link(self, obj):
        if obj.map_url:
            return f"<a href='{obj.map_url}' target='_blank'>Open Map</a>"
        return "-"
    map_link.allow_tags = True
    map_link.short_description = 'Google Map'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)  # Optional custom CSS if needed
        }



# @admin.register(TouristPlace)
# class TouristPlaceAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#         'city_name',
#         'distance_from_main_city',
#         'location_inside_city',
#         'map_link',
#         'created_at'
#     )
#     list_filter = ('city',)
#     search_fields = ('name', 'city__name', 'location_inside_city')
#     ordering = ('city', 'name')

#     def city_name(self, obj):
#         return obj.city.name if obj.city else "-"
#     city_name.short_description = 'City'

#     def map_link(self, obj):
#         if obj.map_url:
#             return f"<a href='{obj.map_url}' target='_blank'>Open Map</a>"
#         return "-"
#     map_link.allow_tags = True
#     map_link.short_description = 'Google Map'

#     class Media:
#         css = {
#             'all': ('admin/css/custom_admin.css',)  # Optional custom CSS if needed
#         }
