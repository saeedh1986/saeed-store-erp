from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, StockMoveViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'moves', StockMoveViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
