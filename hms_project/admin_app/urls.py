# admin_app/urls.py - FIXED VERSION WITH LOGIN

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StaffViewSet, login_view, logout_view  # ← Add login/logout

router = DefaultRouter()
router.register(r'staff', StaffViewSet, basename='staff')

app_name = 'admin_app'

urlpatterns = [
    # Authentication endpoints
    path('login/', login_view, name='login'),  # ← ADD THIS
    path('logout/', logout_view, name='logout'),  # ← ADD THIS
    
    # Staff management
    path('', include(router.urls)),
]
