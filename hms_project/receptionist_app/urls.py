from rest_framework.routers import DefaultRouter
from .import views

router = DefaultRouter()
# router.register(r'doctors', views.DoctorViewSet)
router.register(r'patients', views.PatientViewSet)
router.register(r'appointments', views.AppointmentViewSet)
router.register(r'billgenerations', views.BillGenerationViewSet)
urlpatterns = router.urls