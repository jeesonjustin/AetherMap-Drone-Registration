from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

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
