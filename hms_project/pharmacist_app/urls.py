from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicineViewSet, MedicineStockViewSet

router = DefaultRouter()
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'medicine-stock', MedicineStockViewSet, basename='medicine-stock')

urlpatterns = [
    path('', include(router.urls)),
]
