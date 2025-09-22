from django.contrib import admin
from .models import Consultation,Prescription,MedicinePrescription,TestPrescription

# Register your models here.
admin.site.register(Consultation)
admin.site.register(Prescription)
admin.site.register(MedicinePrescription)
admin.site.register(TestPrescription)