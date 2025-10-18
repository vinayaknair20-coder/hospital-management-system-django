# pharmacist_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicineCategoryViewSet, MedicineViewSet, MedicineBatchViewSet, StockMovementViewSet

router = DefaultRouter()
router.register(r'categories', MedicineCategoryViewSet, basename='medicine-category')
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'batches', MedicineBatchViewSet, basename='medicine-batch')
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movement')

app_name = 'pharmacist_app'

urlpatterns = [
    path('', include(router.urls)),
]
