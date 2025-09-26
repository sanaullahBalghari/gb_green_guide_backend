from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('admin/', admin.site.urls),

    # Accounts
    path('api/accounts/', include('accounts.urls')),

    # Core (cities, regions, events, tourist places, etc.)
    path('api/core/', include('core.urls')), 

    # Business (restaurants, etc.)
    path('api/business/', include('Business.urls')),

    # eCommerce (products, cart, orders, categories, etc.)
    path('api/ecommerce/', include('ecommerce.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
