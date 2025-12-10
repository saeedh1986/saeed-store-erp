from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet

router = DefaultRouter()
# Script hits /api/v1/customers NOT /api/v1/contacts/customers
# Wait, script hits `{ERP_API_URL}/customers`.
# So main urls.py should route `/api/v1/customers` to this viewset?
# Or I can register it here as '' (empty string) if I route specifically in main.
# Let's route /api/v1/customers (plural) in main config directly to this viewset?
# Or keep structure cleaner: /api/v1/contacts/customers
# The script expects /customers directly under api/v1.
# So I will handle that in main urls.py or here.

router.register(r'', ContactViewSet) # This makes it /api/v1/customers/ (if included there)

urlpatterns = [
    path('', include(router.urls)),
]
