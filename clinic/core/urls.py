from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
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
        "panel/appointments/",
        views.admin_appointments,
        name="admin_appointments",
    ),
]


