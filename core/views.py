from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse, HttpResponse # ✅ Import HttpResponse
import json
import uuid
from datetime import date, timedelta
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from .models import ServiceProvider, Service
from .forms import ServiceProviderForm, ServiceForm




# ✅ --- START OF CHANGES ---
# 1. Import the new library
from io import BytesIO
# 2. We no longer need WeasyPrint
# from weasyprint import HTML
# ✅ --- END OF CHANGES ---

# Import all necessary models
from .forms import DroneRegistrationForm
from .models import (
    CustomUser, Role, DroneRegistration, District, 
    Municipality, ApprovedDroneModel, CertificationRuleSet
)

from django.http import HttpResponse, Http404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from .models import DroneRegistration
from datetime import datetime
# ... (All your other views like load_municipalities, login, signup, etc. remain exactly the same) ...

def load_municipalities(request):
    district_id = request.GET.get('district_id')
    municipalities = Municipality.objects.filter(district_id=district_id).order_by('name') if district_id else Municipality.objects.none()
    data = [{"id": m.id, "name": m.name, "is_red_zone": m.is_red_zone} for m in municipalities]
    return JsonResponse(data, safe=False)



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
            role_name = user.role.name.lower() if user.role else ""
            if role_name == "farmer":
                return redirect("farmer_dashboard")
            elif role_name == "service_provider":
                return redirect("service_provider_dashboard")
            elif role_name == "drone_user":
                return redirect("drone_dashboard")
            elif role_name == "admin":
                return redirect("admin_dashboard")
            else:
                return redirect("index")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
    return render(request, "login.html")

def signup_view(request):
    print("Signup view accessed", request.method)
    if request.method == "POST":
        form = request.POST
        username = form.get("username", "").strip()
        email = form.get("email", "").strip()
        password = form.get("password1", "")
        password2 = form.get("password2", "")
        role_name = form.get("role", "").strip().lower()
        print(f"Received data - Username: {username}, Email: {email}, Role: {role_name}")
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")
        
        try:
            role_instance = Role.objects.get(name__iexact=role_name)
            print("Role instance found:", role_instance)
            user = CustomUser.objects.create_user(username=username, email=email, password=password, role=role_instance)
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")
        except Role.DoesNotExist:
            messages.error(request, "Selected role does not exist.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect("signup")

    return render(request, "signup.html")

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("index")

@login_required
def drone_dashboard(request):
    user_registrations = DroneRegistration.objects.filter(user=request.user).order_by('-created_at')
    context = {'registrations': user_registrations}
    return render(request, "drone_dashboard.html", context)

def service_provider_dashboard(request):
    return render(request, "service_provider.html")

def farmer_dashboard(request):
    return render(request, "farmers_dashboard.html")

@login_required
def admin_dashboard(request):
    total_users = CustomUser.objects.count()
    drone_role = Role.objects.filter(name__iexact="drone_user").first()
    farmer_role = Role.objects.filter(name__iexact="farmer").first()
    provider_role = Role.objects.filter(name__iexact="service_provider").first()
    drone_users = CustomUser.objects.filter(role=drone_role).count() if drone_role else 0
    farmers = CustomUser.objects.filter(role=farmer_role).count() if farmer_role else 0
    providers = CustomUser.objects.filter(role=provider_role).count() if provider_role else 0
    all_users = CustomUser.objects.select_related("role").order_by("-date_joined")
    drone_registrations = DroneRegistration.objects.select_related('user').order_by('-created_at')
    # 🟩 Fetch Service Provider Info
    service_providers = ServiceProvider.objects.select_related('user').all()
    provider_role = Role.objects.filter(name__iexact="service_provider").first()
    a=CustomUser.objects.filter(role=provider_role)
    
    print("Service Providers:", service_providers)
    provider_data = []
    for provider in a:
        services = Service.objects.filter(provider_id=provider.id)
        provider_data.append({
            'id': provider.id,
            'provider_name': provider.first_name + " " + provider.last_name if provider.first_name and provider.last_name else provider.username,
            'email': provider.email,
            'service_count': services.count(),
            'services': services,
            'registered_on': provider.date_joined,
        })
    context = {
        "total_users": total_users, "drone_users": drone_users, "farmers": farmers,
        "providers": providers, "all_users": all_users, "drone_registrations": drone_registrations,
        "service_providers": provider_data,
    }
    return render(request, "admin_dashboard.html", context)

@login_required
def drone_registration_view(request):
    if request.method == "POST":
        form = DroneRegistrationForm(request.POST)
        print("Form valid?", form.is_valid())
        if form.is_valid():
            reg = form.save(commit=False)
            reg.user = request.user
            reg.full_name = request.user.get_full_name() or request.user.username
            reg.email = request.user.email
            
            reg.run_validation_checks()  # optional
            reg.save()
            
            messages.success(request, "Drone registration submitted and is now pending review.")
            return redirect("drone_dashboard")
        else:
            # ✅ Print errors here to debug why form is invalid
            print(form.errors)
            messages.error(request, "Please correct the errors shown below.")
            return render(request, "drone_user_reg.html", {"form": form})
    else:
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email
        }
        form = DroneRegistrationForm(initial=initial_data)

    return render(request, "drone_user_reg.html", {"form": form})



@login_required
def generate_certificate(request, registration_id):
    if not (request.user.is_superuser or (request.user.role and request.user.role.name.lower() == "admin")):
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
    if request.method == "POST":
        try:
            registration = get_object_or_404(DroneRegistration, id=registration_id)
            data = json.loads(request.body)
            new_status = data.get("status")
            if new_status == "Approved":
                registration.application_status = new_status
                registration.save()
                return JsonResponse({"success": True, "new_status": new_status})
            else:
                return JsonResponse({"success": False, "error": "This function is only for approving applications."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})
    # print("Generating certificate for registration ID:", registration_id)
    # if not (request.user.is_superuser or (request.user.role and request.user.role.name.lower() == "admin")):
    #     return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    # reg = get_object_or_404(DroneRegistration, id=registration_id)
    # if reg.application_status == 'Approved':
    #     return JsonResponse({'success': False, 'error': 'This registration has already been approved.'})
    # # if reg.pre_approval_status != "Checks Passed":
    # #     error_message = f'Cannot generate certificate. Automated checks failed with the following issues:\n\n{reg.validation_notes}'
    # #     return JsonResponse({'success': False, 'error': error_message})

    # try:
    #     # reg.application_status = 'Approved'
    #     # reg.approval_certificate_id = str(uuid.uuid4()).split('-')[0].upper()
    #     # reg.certificate_valid_from = date.today()
    #     # reg.certificate_valid_to = date.today() + timedelta(days=30)
        
    #     # # ✅ --- START OF PDF GENERATION CHANGES ---
    #     # html_string = render_to_string('certificate_template.html', {'reg': reg})
        
    #     # # Create a PDF file in memory
    #     # result = BytesIO()
    #     # pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
        
    #     # if not pdf.err:
    #     #     # Save the generated PDF to the certificate_file field
    #     #     file_name = f"certificate-{reg.approval_certificate_id}.pdf"
    #     #     reg.certificate_file.save(file_name, ContentFile(result.getvalue()), save=True)
    #     #     return JsonResponse({'success': True, 'file_url': reg.certificate_file.url})
    #     # else:
    #     #     return JsonResponse({'success': False, 'error': f'PDF generation error: {pdf.err}'})
    #     # # ✅ --- END OF PDF GENERATION CHANGES ---
    #         registration = get_object_or_404(DroneRegistration, id=registration_id)
    #         data = json.loads(request.body)
    #         new_status = data.get("status")
    #         if new_status == "Approved":
    #             registration.application_status = new_status
    #             registration.save()
    #             return JsonResponse({"success": True, "new_status": new_status})
    #         else:
    #             return JsonResponse({"success": False, "error": "This function is only for approving applications."})

    # except Exception as e:
    #     print("error..!", e)
    #     return JsonResponse({'success': False, 'error': f'An unexpected error occurred: {str(e)}'})

@login_required
def update_drone_status(request, registration_id):
    if not (request.user.is_superuser or (request.user.role and request.user.role.name.lower() == "admin")):
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
    if request.method == "POST":
        try:
            registration = get_object_or_404(DroneRegistration, id=registration_id)
            data = json.loads(request.body)
            new_status = data.get("status")
            if new_status == "Rejected":
                registration.application_status = new_status
                registration.save()
                # admin_dashboard(request)
                
                # return redirect(reverse('admin_dashboard'))
                return JsonResponse({"success": True, "new_status": new_status})
            else:
                return JsonResponse({"success": False, "error": "This function is only for rejecting applications."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})
    
def download_drone_pdf(request, pk):
    try:
        drone = DroneRegistration.objects.get(pk=pk)
    except DroneRegistration.DoesNotExist:
        raise Http404("Drone registration not found")

    # Response setup
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="drone_{drone.id}.pdf"'

    # Create PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 80

    # Header
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, y, "GOVERNMENT OF INDIA")
    y -= 20
    p.drawCentredString(width / 2, y, "DIRECTORATE GENERAL OF CIVIL AVIATION (DGCA)")
    y -= 20
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, "AetherMap – Drone Registration Certificate")
    y -= 40

    p.setFont("Helvetica", 12)

    # --- Certificate Details ---
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Certificate Details")
    y -= 20
    p.setFont("Helvetica", 11)

    p.drawString(70, y, f"Date of Issue: {drone.created_at.strftime('%Y-%m-%d') if drone.created_at else 'N/A'}")
    y -= 20
    p.drawString(70, y, f"Validity From: {drone.flight_start_time.strftime('%Y-%m-%d') if drone.flight_start_time else 'N/A'}")
    y -= 20
    p.drawString(70, y, f"Expired On: {drone.flight_end_time.strftime('%Y-%m-%d') if drone.flight_end_time else 'N/A'}")
    y -= 40

    # --- Drone Details ---
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Drone – Aircraft Details")
    y -= 20
    p.setFont("Helvetica", 11)
    p.drawString(70, y, f"UIN: {drone.id or 'Pending'}")
    y -= 20
    p.drawString(70, y, f"Model: {drone.drone_model}")
    y -= 20
    p.drawString(70, y, f"Serial Number: {drone.drone_serial_number}")
    y -= 20
    p.drawString(70, y, f"Purpose of Flying: {drone.drone_purpose}")
    y -= 40

    # --- Owner / Operator Details ---
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Owner / Operator Details")
    y -= 20
    p.setFont("Helvetica", 11)
    p.drawString(70, y, f"Name: {drone.full_name}")
    y -= 20
    p.drawString(70, y, f"Contact Number: {drone.phone_number}")
    y -= 20
    p.drawString(70, y, f"Email ID: {drone.email}")
    y -= 20
    p.drawString(70, y, f"Operator / Registration ID: {drone.full_name}/{drone.user.id}")
    y -= 40

    # --- Conditions & Remarks ---
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Conditions & Remarks")
    y -= 20
    p.setFont("Helvetica", 10)
    conditions = [
        "Operation as per Drone Rules, 2021 and all DGCA / Digital Sky regulations.",
        "Marking the drone with the UIN in a visible, durable manner.",
        "Use of NPNT (No Permission, No Takeoff) system for all flight permissions.",
        "Restrictions on zones (Green / Yellow / Red), altitude limits, time & area of operations must be strictly followed.",
        "The DGCA / Digital Sky reserves the right to suspend / revoke this certificate upon non-compliance."
    ]
    for cond in conditions:
        p.drawString(70, y, f"- {cond}")
        y -= 15
    y -= 25

    # --- Declaration ---
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Declaration (By the Applicant/Operator)")
    y -= 20

    p.setFont("Helvetica", 10)
    declaration = (
    f"I, {drone.full_name}, hereby declare that the information provided is true and correct. "
    f"I agree to operate the drone in full compliance with the Drone Rules, 2021 and all DGCA / AetherMap "
    f"regulations. I understand that any violation or misuse may lead to suspension or cancellation of this certificate."
)

# Split the declaration into multiple lines if too long
    from reportlab.lib.utils import simpleSplit
    lines = simpleSplit(declaration, "Helvetica", 10, 500)  # 500 is max width in points

    for line in lines:
        p.drawString(50, y, line)
        y -= 20  # adjust line spacing

    

    # Finalize
    p.showPage()
    p.save()
    return response

# ---- Provider Profile ----
@login_required
def provider_profile(request):
    try:
        profile = request.user.provider_profile
    except ServiceProvider.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = ServiceProviderForm(request.POST, instance=profile)
        if form.is_valid():
            provider_profile = form.save(commit=False)
            provider_profile.user = request.user
            provider_profile.save()
            messages.success(request, "Profile saved successfully!")
            return redirect('provider_profile')
    else:
        form = ServiceProviderForm(instance=profile)

    return render(request, 'provider_profile.html', {'form': form})


# ---- Service Management ----
@login_required
def service_list(request):
    services = Service.objects.filter(provider=request.user)
    return render(request, 'service_list.html', {'services': services})

@login_required
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.save()
            messages.success(request, "Service added successfully!")
            return redirect('service_list')
    else:
        form = ServiceForm()
    return render(request, 'add_service.html', {'form': form})

@login_required
def edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service updated successfully!")
            return redirect('service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'add_service.html', {'form': form, 'edit': True})

@login_required
def delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    service.delete()
    messages.success(request, "Service deleted successfully!")
    return redirect('service_list')

# 🟢 View single provider details
@login_required
# @user_passes_test(admin_required)
def provider_detail(request, pk):
    provider = get_object_or_404(ServiceProvider, pk=pk)
    services = Service.objects.filter(provider=provider.user)
    return render(request, 'provider_detail.html', {'provider': provider, 'services': services})

# 🔵 Edit provider
@login_required

def edit_provider(request, pk):
    provider_user = get_object_or_404(CustomUser, pk=pk)
    if request.method == "POST":
        provider_user.full_name = request.POST.get("full_name", provider_user.full_name)
        provider_user.email = request.POST.get("email", provider_user.email)
        provider_user.save()
        messages.success(request, "Provider details updated successfully.")
        return redirect("admin_dashboard")

    return render(request, "edit_provider.html", {"provider_user": provider_user})

# 🔴 Delete provider
@login_required
# @user_passes_test(admin_required)
def delete_provider(request, pk):
    provider = get_object_or_404(ServiceProvider, pk=pk)
    provider.delete()
    messages.success(request, 'Service Provider deleted successfully.')
    return redirect('admin_dashboard')