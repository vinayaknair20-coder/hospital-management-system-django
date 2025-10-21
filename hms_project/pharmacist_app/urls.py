# pharmacy/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MedicineCategoryViewSet, 
    MedicineViewSet, 
    MedicineBatchViewSet, 
    StockMovementViewSet,
    dashboard_stats,  # ← ADD THIS
    prescription_list  # ← ADD THIS
)

router = DefaultRouter()
router.register(r'categories', MedicineCategoryViewSet, basename='medicine-category')
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'batches', MedicineBatchViewSet, basename='medicine-batch')
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movement')

app_name = 'pharmacist_app'

urlpatterns = [
    # Dashboard endpoints
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),  # ← ADD THIS
    path('prescriptions/', prescription_list, name='prescription-list'),  # ← ADD THIS
    
    # Router URLs
    path('', include(router.urls)),
]
