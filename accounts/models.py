from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Account used to sign in. Survey responses are NOT linked to this model,
    so the anonymity rule (BR-02) in the SDD is preserved."""

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        COUNSELOR = "COUNSELOR", "Guidance Counselor"
        STUDENT = "STUDENT", "College Student"

    email = models.EmailField("email address", unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^[0-9+()\-\s]{7,20}$", "Enter a valid contact number.")],
    )
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True)

    def save(self, *args, **kwargs):
        # Superusers made with `createsuperuser` always land on the admin dashboard.
        if self.is_superuser:
            self.role = self.Role.ADMIN
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    @property
    def dashboard_name(self):
        return f"dashboard:{self.role.lower()}"

    def __str__(self):
        return self.username
