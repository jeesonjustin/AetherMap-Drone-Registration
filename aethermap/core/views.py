from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .forms import SignUpForm
from .models import CustomUser


def index_view(request):
    return render(request, "index.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back {username} 👋")

            # Redirect based on role (stored in CustomUser)
            try:
                profile = user.profile
                if profile.role == "farmer":
                    return redirect("farmer_dashboard")
                elif profile.role == "service_provider":
                    return redirect("service_provider_dashboard")
                elif profile.role == "drone_user":
                    return redirect("drone_user_dashboard")
                else:
                    return redirect("home")
            except CustomUser.DoesNotExist:
                return redirect("home")

        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "login.html")


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        role = request.POST.get("role", "").strip()

        # ✅ Required fields
        if not all([username, email, password1, password2, role]):
            messages.error(request, "All fields are required.")
            return redirect("signup")

        # ✅ Email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return redirect("signup")

        # ✅ Password match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        # ✅ Username uniqueness
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("signup")

        # ✅ Email uniqueness
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("signup")

        # ✅ Role check
        if role not in ["drone_user", "service_provider", "farmer"]:
            messages.error(request, "Invalid role selected.")
            return redirect("signup")

        # ✅ Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        # ✅ Create CustomUser
        CustomUser.objects.create(user=user, role=role)

        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")

    return render(request, "signup.html")

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")

def drone_dashboard(request):
    return render(request, "drone_dashboard.html")