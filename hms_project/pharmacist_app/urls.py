"""
PHARMACIST APP URLs
URL patterns for all pharmacy endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'categories', views.MedicineCategoryViewSet, basename='medicinecategory')
router.register(r'suppliers', views.SupplierViewSet, basename='supplier')
router.register(r'medicines', views.MedicineViewSet, basename='medicine')
router.register(r'stock', views.MedicineStockViewSet, basename='medicinestock')
router.register(r'alerts', views.StockAlertViewSet, basename='stockalert')
router.register(r'prescriptions', views.PrescriptionViewSet, basename='prescription')
router.register(r'sales', views.SaleViewSet, basename='sale')
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')

# URL patterns
urlpatterns = [
    # API routes
    path('api/', include(router.urls)),
    
    # Custom endpoints (if needed)
    path('api/reports/inventory/', views.InventoryReportView.as_view(), name='inventory-report'),
    path('api/reports/sales/', views.SalesReportView.as_view(), name='sales-report'),
    path('api/utils/generate-alerts/', views.GenerateAlertsView.as_view(), name='generate-alerts'),
]

app_name = 'pharmacist_app'
