from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import DroneRegistration, District, Municipality
from django import forms
from .models import ServiceProvider, Service

# -----------------------------
# User Signup Form
# -----------------------------
class SignUpForm(UserCreationForm):
    ROLE_CHOICES = [
        ("drone_user", "Drone User"),
        ("service_provider", "Service Provider"),
        ("farmer", "Farmer"),
    ]

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "role"]


# -----------------------------
# Drone Registration Form
# -----------------------------
class DroneRegistrationForm(forms.ModelForm):
    flight_district = forms.ModelChoiceField(
        queryset=District.objects.all(),
        label="Flight District",
        empty_label="Select a District",
        widget=forms.Select(attrs={"class": "form-select rounded"})
    )
    flight_municipality = forms.ModelChoiceField(
        queryset=Municipality.objects.none(),
        label="Flight Municipality",
        empty_label="Select a District First",
        widget=forms.Select(attrs={"class": "form-select rounded"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make full_name and email optional (we'll set them from server)
        self.fields['full_name'].required = False
        self.fields['email'].required = False

        # Dynamically populate municipalities based on selected district
        if 'flight_district' in self.data:
            try:
                district_id = int(self.data.get('flight_district'))
                self.fields['flight_municipality'].queryset = Municipality.objects.filter(
                    district_id=district_id
                ).order_by('name')
            except (ValueError, TypeError):
                self.fields['flight_municipality'].queryset = Municipality.objects.none()
        elif self.instance.pk and self.instance.flight_district:
            self.fields['flight_municipality'].queryset = self.instance.flight_district.municipality_set.order_by('name')

    class Meta:
        model = DroneRegistration
        fields = [
            "full_name", "email", "phone_number", "date_of_birth",
            "drone_model", "drone_serial_number", "drone_purpose",
            "flight_district", "flight_municipality",
            "flight_start_time", "flight_end_time", "flight_reason",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control rounded", "readonly": True}),
            "email": forms.EmailInput(attrs={"class": "form-control rounded", "readonly": True}),
            "phone_number": forms.TextInput(attrs={"class": "form-control rounded", "placeholder": "Phone Number"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control rounded", "type": "date"}),
            "drone_model": forms.TextInput(attrs={"class": "form-control rounded", "placeholder": "e.g., DJI Mavic 3"}),
            "drone_serial_number": forms.TextInput(attrs={"class": "form-control rounded", "placeholder": "Unique Serial #"}),
            "drone_purpose": forms.Select(attrs={"class": "form-select rounded"}),
            "flight_start_time": forms.DateTimeInput(attrs={"class": "form-control rounded", "type": "datetime-local"}),
            "flight_end_time": forms.DateTimeInput(attrs={"class": "form-control rounded", "type": "datetime-local", "readonly": True}),
            "flight_reason": forms.Textarea(attrs={"class": "form-control rounded", "rows": 3, "placeholder": "Describe the purpose of the flight..."}),
        }
class ServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = ['company_name', 'license_number', 'service_area']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'service_area': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'tags', 'price', 'availability']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'availability': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


