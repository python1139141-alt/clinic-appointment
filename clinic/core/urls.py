from django.urls import path
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("doctors/", views.doctor_list, name="doctor_list"),
    path("doctors/<int:pk>/", views.doctor_detail, name="doctor_detail"),
    path("book/", views.book_appointment, name="book_appointment"),
    path("book/success/", views.appointment_success, name="appointment_success"),
    path(
        "appointments/history/",
        views.appointment_history,
        name="appointment_history",
    ),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("panel/doctors/", views.admin_doctors, name="admin_doctors"),
    path(
        "panel/doctors/<int:pk>/edit/",
        views.admin_doctor_edit,
        name="admin_doctor_edit",
    ),
    path(
        "panel/doctors/<int:pk>/delete/",
        views.admin_doctor_delete,
        name="admin_doctor_delete",
    ),
    path(
        "panel/specializations/",
        views.admin_specializations,
        name="admin_specializations",
    ),
    path(
        "panel/specializations/<int:pk>/edit/",
        views.admin_specialization_edit,
        name="admin_specialization_edit",
    ),
    path(
        "panel/specializations/<int:pk>/delete/",
        views.admin_specialization_delete,
        name="admin_specialization_delete",
    ),
    # JSON endpoints for AJAX/modal interactions
    path(
        "api/specializations/<int:pk>/",
        views.admin_specialization_detail,
        name="api_specialization_detail",
    ),
    path(
        "panel/appointments/",
        views.admin_appointments,
        name="admin_appointments",
    ),
]


