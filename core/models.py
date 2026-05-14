from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from datetime import date, timedelta
import uuid

# --- User and Role Models ---
# These models define the different types of users in your system.

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.username

# --- Rule Management Models (Editable by Admin) ---
# These models store the rules that the system uses for validation.
# An admin can change these without needing to change the code.

class ApprovedDroneModel(models.Model):
    model_name = models.CharField(max_length=100, unique=True, help_text="e.g., DJI Mavic 3 Pro")
    manufacturer = models.CharField(max_length=100, help_text="e.g., DJI")
    
    def __str__(self):
        return self.model_name

class CertificationRuleSet(models.Model):
    rule_name = models.CharField(max_length=100, default="Default Drone Rules")
    min_required_age = models.PositiveIntegerField(default=18, help_text="Minimum age required for a drone pilot certificate.")
    
    def __str__(self):
        return self.rule_name

# --- Location Models ---
# These models store the geographic data for flight planning.

class District(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Municipality(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_red_zone = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# --- Main Registration Model ---
# This is the core model that brings everything together.

class DroneRegistration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="drone_registrations")
    
    # User Details
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    date_of_birth = models.DateField()

    # Drone Details
    drone_model = models.CharField(max_length=100)
    drone_serial_number = models.CharField(max_length=100, unique=True)
    drone_purpose = models.CharField(max_length=50, choices=[
        ("Recreational", "Recreational"), ("Commercial", "Commercial"), ("Research", "Research"),
        ("Agriculture", "Agriculture"), ("Delivery", "Delivery"), ("Other", "Other"),
    ])
    
    # Flight Details
    flight_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    flight_municipality = models.ForeignKey(Municipality, on_delete=models.SET_NULL, null=True)
    flight_start_time = models.DateTimeField()
    flight_end_time = models.DateTimeField(blank=True, null=True)
    flight_reason = models.TextField()

    # --- NEW: Automated Validation Fields ---
    # These fields store the results of the automatic checks.
    pre_approval_status = models.CharField(max_length=50, default="Pending Review")
    validation_notes = models.TextField(blank=True, null=True, help_text="Stores reasons for validation failure.")
    
    # System & Certificate Fields
    application_status = models.CharField(max_length=20, default="Pending", choices=[
        ("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected"),
    ])
    approval_certificate_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    certificate_valid_from = models.DateField(blank=True, null=True)
    certificate_valid_to = models.DateField(blank=True, null=True)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.drone_model}"

    # --- NEW: The "Brain" of the Validation Logic ---
    # This method runs all the checks based on the rules in the database.
    def run_validation_checks(self):
        try:
            # Get the latest set of rules defined by the admin
            rules = CertificationRuleSet.objects.latest('id')
        except CertificationRuleSet.DoesNotExist:
            self.pre_approval_status = "Failed"
            self.validation_notes = "System Error: No certification rules are defined by the admin."
            self.save()
            return

        checks_passed = True
        notes = []

        # 1. Age Check
        today = date.today()
        age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        if age < rules.min_required_age:
            checks_passed = False
            notes.append(f"Age Check Failed: Applicant is {age}, but the minimum required age is {rules.min_required_age}.")

        # 2. Drone Model Check
        if not ApprovedDroneModel.objects.filter(model_name__iexact=self.drone_model).exists():
            checks_passed = False
            notes.append(f'Model Check Failed: The drone model "{self.drone_model}" is not on the approved list.')

        # 3. Flight Zone Check
        if self.flight_municipality and self.flight_municipality.is_red_zone:
            checks_passed = False
            notes.append("Zone Check Failed: The selected municipality is a designated Red Zone where flights are not permitted.")

        # Update the status fields based on the results of the checks
        if checks_passed:
            self.pre_approval_status = "Checks Passed"
            self.validation_notes = "All automated checks were successful. Ready for admin approval."
        else:
            self.pre_approval_status = "Checks Failed"
            self.validation_notes = "\n".join(notes)
        
        self.save()

# Farmer profile
class Farmer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="farmer_profile")
    farm_location = models.CharField(max_length=255)
    crops_grown = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username


# Drone service provider profile
class ServiceProvider(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="provider_profile")
    company_name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100)
    service_area = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.company_name


# Request model for farmers to request services
class FarmerRequest(models.Model):
    farmer = models.ForeignKey("Farmer", on_delete=models.CASCADE)
    provider = models.ForeignKey("ServiceProvider", on_delete=models.CASCADE)
    service_description = models.TextField()
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )

    def __str__(self):
        return f"{self.farmer.user.username} -> {self.provider.company_name}"


# Optional service listing
class Service(models.Model):
    provider = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="services")
    title = models.CharField(max_length=150)
    description = models.TextField()
    tags = models.CharField(max_length=255, blank=True)  # Add this
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)     # Add this

    def __str__(self):
        return self.title