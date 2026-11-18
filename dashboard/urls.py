from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("admin/", views.admin_dashboard, name="admin"),
    path("counselor/", views.counselor_dashboard, name="counselor"),
    path("student/", views.student_dashboard, name="student"),
]
