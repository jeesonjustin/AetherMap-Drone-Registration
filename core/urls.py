from django.urls import path
from . import views


urlpatterns = [
    # 🏠 General Views
    path("", views.index_view, name="index"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

     # 🛸 Drone User
    path("drone/dashboard/", views.drone_dashboard, name="drone_dashboard"),
    path("drone/register/", views.drone_registration_view, name="drone_registration"),
    path("drone/<int:pk>/pdf/", views.download_drone_pdf, name="download_drone_pdf"),
    path("dashboard/update_status/<int:registration_id>/", views.update_drone_status, name="update_status"),
    path("dashboard/generate-certificate/<int:registration_id>/", views.generate_certificate, name="generate_certificate"),
    path("ajax/load-municipalities/", views.load_municipalities, name="ajax_load_municipalities"),

    # 🚜 Farmer
    path("farmer/dashboard/", views.farmer_dashboard, name="farmer_dashboard"),

     # 🧩 Admin Panel
    path("admin-panel/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path('admin-panel/providers/<int:pk>/', views.provider_detail, name='provider_detail'),
    path('admin-panel/providers/<int:pk>/edit/', views.edit_provider, name='edit_provider'),
    path('admin-panel/providers/<int:pk>/delete/', views.delete_provider, name='delete_provider'),
    path('admin-panel/services/<int:pk>/edit/', views.edit_service, name='edit_service'),
    path('admin-panel/services/<int:pk>/delete/', views.delete_service, name='delete_service'),
    
    # 🧑‍💼 Service Provider
    path("service-provider/dashboard/", views.service_provider_dashboard, name="service_provider_dashboard"),
    path('provider/profile/', views.provider_profile, name='provider_profile'),
    path('provider/services/', views.service_list, name='service_list'),
    path('provider/services/add/', views.add_service, name='add_service'),
    path('provider/services/<int:pk>/edit/', views.edit_service, name='edit_service'),
    path('provider/services/<int:pk>/delete/', views.delete_service, name='delete_service'),

    
    
]
# path('services/', views.service_list, name='service_list'),
#     path('services/add/', views.add_service, name='add_service'),
#     path('services/<int:pk>/edit/', views.edit_service, name='edit_service'),
#     path('services/<int:pk>/delete/', views.delete_service, name='delete_service'),