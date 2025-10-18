# hms_project/urls.py - COMPLETE FIXED VERSION
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """API Root - Welcome Page"""
    return JsonResponse({
        'message': 'Hospital Management System API',
        'version': '1.0',
        'endpoints': {
            'admin_panel': '/admin/',
            'admin_api': '/api/admin/',
            'receptionist_api': '/api/receptionist/',
            'pharmacist_api': '/api/pharmacist/',
            'doctor_api': '/api/doctor/',
            'lab_tech_api': '/api/lab-tech/',
            'authentication': '/api/auth/'
        },
        'documentation': '/api/docs/'
    })

urlpatterns = [
    path('', api_root, name='api-root'),  # ✅ ROOT URL
    path('admin/', admin.site.urls),
    path('api/admin/', include('admin_app.urls')),
    path('api/receptionist/', include('receptionist_app.urls')),
    path('api/pharmacist/', include('pharmacist_app.urls')),
    path('api/doctor/', include('doctor_app.urls')),
    path('api/lab-tech/', include('labTech_app.urls')),
]
