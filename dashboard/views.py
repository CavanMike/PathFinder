from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render

from accounts.decorators import role_required

User = get_user_model()


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    return redirect("accounts:login")


@login_required
def dashboard_home(request):
    """Send each user to the dashboard for their own role."""
    return redirect(request.user.dashboard_name)


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    counts = {row["role"]: row["n"] for row in User.objects.values("role").annotate(n=Count("id"))}
    context = {
        "total_users": sum(counts.values()),
        "student_count": counts.get(User.Role.STUDENT, 0),
        "counselor_count": counts.get(User.Role.COUNSELOR, 0),
        "admin_count": counts.get(User.Role.ADMIN, 0),
        "recent_users": User.objects.order_by("-date_joined")[:8],
    }
    return render(request, "dashboard/admin.html", context)


@role_required(User.Role.COUNSELOR)
def counselor_dashboard(request):
    return render(request, "dashboard/counselor.html")


@role_required(User.Role.STUDENT)
def student_dashboard(request):
    return render(request, "dashboard/student.html")
