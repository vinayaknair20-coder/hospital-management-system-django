
from django.contrib import admin
from .models import Patient,Doctor, Appointment, Bill_Generation

# Register your models here.
class AppointmentInline(admin.TabularInline):
	model = Appointment
	extra = 1

class PatientAdmin(admin.ModelAdmin):
	inlines = [AppointmentInline]

admin.site.register(Patient, PatientAdmin)
# admin.site.register(Doctor)
admin.site.register(Appointment)
class BillGenerationAdmin(admin.ModelAdmin):
	readonly_fields = ('Token',)

admin.site.register(Bill_Generation, BillGenerationAdmin)
