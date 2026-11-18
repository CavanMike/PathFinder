# PathFinder (IM2 Phase 1: Account Feature)

Full-stack Django (templates) + PostgreSQL / Supabase. No SQLite.

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # then edit .env (macOS/Linux: cp)
python manage.py makemigrations accounts
python manage.py migrate
python manage.py createsuperuser   # becomes role ADMIN automatically
python manage.py test
python manage.py runserver
```

### Database
- Local PostgreSQL: create a database named `pathfinder`, then set `DB_*` in `.env`.
- Supabase: Project Settings > Database > Connection string, paste it as `DATABASE_URL`
  and set `DB_SSL_REQUIRE=True`.

## What is included
- `/accounts/register/` registration (role: student or counselor; admins are created by superuser)
- `/accounts/login/`, `/accounts/logout/` (POST)
- `/dashboard/` redirects to `/dashboard/admin/`, `/counselor/` or `/student/`; wrong role gets 403
- `/accounts/profile/` and `/accounts/profile/edit/` (own profile only; photo upload)

## Notes
- Survey responses (next phase) must not reference `accounts.User`, to keep BR-02 anonymity.
- Run `makemigrations accounts` BEFORE the first `migrate` (custom user model).
