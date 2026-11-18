from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()
PW = "Sup3r-Secret-pw!"


def make_user(username, role, email=None, **extra):
    return User.objects.create_user(
        username=username, email=email or f"{username}@example.com", password=PW, role=role, **extra
    )


class RegistrationTests(TestCase):
    def payload(self, **over):
        data = {
            "role": "STUDENT", "username": "maria", "first_name": "Maria", "last_name": "Santos",
            "email": "Maria@Example.com", "contact_number": "09171234567",
            "password1": PW, "password2": PW,
        }
        data.update(over)
        return data

    def test_register_success_hashes_password(self):
        r = self.client.post(reverse("accounts:register"), self.payload(), follow=True)
        self.assertRedirects(r, reverse("accounts:login"))
        self.assertContains(r, "Account created")
        u = User.objects.get(username="maria")
        self.assertNotEqual(u.password, PW)
        self.assertTrue(u.password.startswith("pbkdf2_"))
        self.assertTrue(u.check_password(PW))
        self.assertEqual(u.email, "maria@example.com")
        self.assertEqual(u.role, User.Role.STUDENT)

    def test_password_mismatch(self):
        r = self.client.post(reverse("accounts:register"), self.payload(password2="different-pw-1"))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username="maria").exists())
        self.assertContains(r, "Please fix the errors below")

    def test_invalid_email(self):
        r = self.client.post(reverse("accounts:register"), self.payload(email="not-an-email"))
        self.assertFalse(User.objects.filter(username="maria").exists())
        self.assertEqual(r.status_code, 200)

    def test_required_fields(self):
        r = self.client.post(reverse("accounts:register"), {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_duplicate_username_and_email(self):
        make_user("maria", "STUDENT", email="maria@example.com")
        r = self.client.post(reverse("accounts:register"), self.payload(username="maria2"))
        self.assertContains(r, "email already exists")
        r = self.client.post(reverse("accounts:register"), self.payload(email="other@example.com"))
        self.assertFalse(User.objects.filter(email="other@example.com").exists())

    def test_cannot_self_register_as_admin(self):
        self.client.post(reverse("accounts:register"), self.payload(role="ADMIN"))
        self.assertFalse(User.objects.filter(username="maria").exists())


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.student = make_user("stu", "STUDENT")

    def test_login_redirects_to_role_dashboard(self):
        r = self.client.post(reverse("accounts:login"), {"username": "stu", "password": PW})
        self.assertRedirects(r, reverse("dashboard:home"), fetch_redirect_response=False)
        r = self.client.get(reverse("dashboard:home"))
        self.assertRedirects(r, reverse("dashboard:student"))

    def test_invalid_credentials_show_error(self):
        r = self.client.post(reverse("accounts:login"), {"username": "stu", "password": "wrong"})
        self.assertContains(r, "Invalid username or password")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_ends_session(self):
        self.client.login(username="stu", password=PW)
        r = self.client.post(reverse("accounts:logout"), follow=True)
        self.assertRedirects(r, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_requires_post(self):
        self.client.login(username="stu", password=PW)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)

    def test_protected_pages_redirect_to_login(self):
        for name in ("dashboard:home", "dashboard:student", "dashboard:counselor",
                     "dashboard:admin", "accounts:profile", "accounts:profile_edit"):
            url = reverse(name)
            r = self.client.get(url)
            self.assertRedirects(r, f"{reverse('accounts:login')}?next={url}", msg_prefix=name)


class RoleAccessTests(TestCase):
    def setUp(self):
        self.users = {
            "ADMIN": make_user("adm", "ADMIN"),
            "COUNSELOR": make_user("cou", "COUNSELOR"),
            "STUDENT": make_user("stu", "STUDENT"),
        }

    def test_each_role_only_opens_its_own_dashboard(self):
        for role, user in self.users.items():
            self.client.force_login(user)
            for other in ("ADMIN", "COUNSELOR", "STUDENT"):
                url = reverse(f"dashboard:{other.lower()}")
                expected = 200 if other == role else 403
                self.assertEqual(self.client.get(url).status_code, expected, f"{role} -> {other}")
            self.client.logout()

    def test_home_redirects_by_role(self):
        for role, user in self.users.items():
            self.client.force_login(user)
            r = self.client.get(reverse("dashboard:home"))
            self.assertRedirects(r, reverse(f"dashboard:{role.lower()}"))
            self.client.logout()

    def test_superuser_gets_admin_role(self):
        su = User.objects.create_superuser("root", "root@example.com", PW)
        self.assertEqual(su.role, User.Role.ADMIN)


class ProfileTests(TestCase):
    def setUp(self):
        self.a = make_user("alice", "STUDENT", first_name="Alice", last_name="A")
        self.b = make_user("bob", "COUNSELOR", first_name="Bob", last_name="B")

    def test_profile_shows_only_own_data(self):
        self.client.force_login(self.a)
        r = self.client.get(reverse("accounts:profile"))
        self.assertContains(r, "alice@example.com")
        self.assertNotContains(r, "bob@example.com")

    def test_update_profile(self):
        self.client.force_login(self.a)
        r = self.client.post(reverse("accounts:profile_edit"), {
            "first_name": "Alicia", "last_name": "A", "email": "alicia@example.com",
            "contact_number": "0917 123 4567",
        }, follow=True)
        self.assertRedirects(r, reverse("accounts:profile"))
        self.assertContains(r, "Profile updated")
        self.a.refresh_from_db()
        self.assertEqual(self.a.first_name, "Alicia")
        self.assertEqual(self.a.email, "alicia@example.com")

    def test_cannot_take_another_users_email_or_change_role(self):
        self.client.force_login(self.a)
        r = self.client.post(reverse("accounts:profile_edit"), {
            "first_name": "Alice", "last_name": "A", "email": "BOB@example.com",
            "role": "ADMIN",
        })
        self.assertContains(r, "email already exists")
        self.a.refresh_from_db()
        self.assertEqual(self.a.role, User.Role.STUDENT)
        self.client.post(reverse("accounts:profile_edit"), {
            "first_name": "Alice", "last_name": "A", "email": "alice@example.com", "role": "ADMIN",
        })
        self.a.refresh_from_db()
        self.assertEqual(self.a.role, User.Role.STUDENT)
        self.b.refresh_from_db()
        self.assertEqual(self.b.first_name, "Bob")
