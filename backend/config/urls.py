from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # FUTURE: API URLs will be included here
    path('api/v1/inventory/', include('inventory.urls')),
    path('api/v1/customers/', include('contacts.urls')),
]
