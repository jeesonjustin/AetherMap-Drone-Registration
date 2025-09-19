from django.urls import path
from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("drone/dashboard/", views.drone_dashboard, name="drone_dashboard"),
    path("service-provider/dashboard/", views.service_provider_dashboard, name="service_provider_dashboard"),
]
