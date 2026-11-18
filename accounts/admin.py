from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class PathFinderUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("PathFinder", {"fields": ("role", "contact_number", "profile_photo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("PathFinder", {"fields": ("email", "role")}),
    )
    list_display = ("username", "email", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
