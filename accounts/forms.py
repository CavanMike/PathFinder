from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

MAX_PHOTO_BYTES = 2 * 1024 * 1024


def _unique_email(form, email):
    email = (email or "").strip().lower()
    qs = User.objects.filter(email__iexact=email)
    if form.instance.pk:
        qs = qs.exclude(pk=form.instance.pk)
    if qs.exists():
        raise forms.ValidationError("An account with this email already exists.")
    return email


class RegistrationForm(UserCreationForm):
    # Admin accounts are never self-registered.
    role = forms.ChoiceField(
        label="I am a",
        choices=[
            (User.Role.STUDENT, "College student"),
            (User.Role.COUNSELOR, "Guidance counselor"),
        ],
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "role", "contact_number")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm password"

    def clean_email(self):
        return _unique_email(self, self.cleaned_data.get("email"))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "contact_number", "profile_photo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name", "email"):
            self.fields[name].required = True

    def clean_email(self):
        return _unique_email(self, self.cleaned_data.get("email"))

    def clean_profile_photo(self):
        photo = self.cleaned_data.get("profile_photo")
        if photo and hasattr(photo, "size") and photo.size > MAX_PHOTO_BYTES:
            raise forms.ValidationError("Photo must be 2 MB or smaller.")
        return photo
