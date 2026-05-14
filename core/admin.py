from django.contrib import admin
from .models import (
    DroneRegistration, District, Municipality,
    ApprovedDroneModel, CertificationRuleSet, Role, CustomUser
)

# Register simple models directly so you can manage them in the admin panel.
# This allows you to add/edit Districts, Municipalities, and user Roles.
admin.site.register(District)
admin.site.register(Municipality)
admin.site.register(Role)
admin.site.register(CustomUser)

# This creates a dedicated section in the admin panel for managing approved drones.
@admin.register(ApprovedDroneModel)
class ApprovedDroneModelAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'manufacturer')
    search_fields = ('model_name', 'manufacturer')

# This creates a section for editing the certification rules, like minimum age.
@admin.register(CertificationRuleSet)
class CertificationRuleSetAdmin(admin.ModelAdmin):
    list_display = ('rule_name', 'min_required_age')

# This upgrades the main DroneRegistration view in the admin panel.
@admin.register(DroneRegistration)
class DroneRegistrationAdmin(admin.ModelAdmin):
    # This determines the columns shown in the registration list.
    list_display = (
        "id",
        "full_name",
        "application_status",
        "pre_approval_status",  # ✅ Shows the result of the automatic checks.
        "flight_district",
        "created_at"
    )
    
    # These are the filters that appear on the right-hand side.
    list_filter = (
        "application_status",
        "pre_approval_status",  # ✅ Allows admin to filter by "Checks Passed" or "Checks Failed".
        "flight_district"
    )
    
    # This defines the fields you can search by.
    search_fields = (
        "full_name",
        "drone_serial_number",
        "user__username"
    )
    
    # This prevents admins from manually changing the results of the automated checks.
    readonly_fields = (
        'pre_approval_status',
        'validation_notes'
    )