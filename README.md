## Clinic Appointment System (Django + Bootstrap)

A simple but polished clinic appointment portal built with **Python + Django**, SQLite, and **Bootstrap**.  
Frontend is fully in English with a modern UI and subtle animations, and it runs 100% fine on **PythonAnywhere**.

### Features

- **Patient side**
  - Home page with stats and featured doctors
  - Doctors list + filter by specialization
  - Doctor detail page
  - Appointment booking form with validation
  - Appointment history (by email)
- **Admin side**
  - Django default admin (full power)
  - Custom admin dashboard (`/admin-dashboard/`)
  - Manage doctors, specializations, appointments
  - Change appointment status (Pending, Approved, Completed)

---

## 1. Local Setup (Windows)

1. **Clone / copy project**
   - Put the project inside e.g. `E:\web-project`

2. **Create and activate virtualenv**

```powershell
cd E:\web-project
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**

```powershell
pip install -r requirements.txt
```

4. **Apply migrations**

```powershell
cd clinic
python manage.py migrate
```

5. **Create superuser**

```powershell
python manage.py createsuperuser
```

6. **Run development server**

```powershell
python manage.py runserver
```

Open in browser:
- `http://127.0.0.1:8000/` → patient frontend
- `http://127.0.0.1:8000/admin/` → Django admin
- `http://127.0.0.1:8000/admin-dashboard/` → custom admin dashboard

---

## 2. PythonAnywhere Deployment (Quick Guide)

1. **Upload code**
   - Push to GitHub **or**
   - Zip the project and upload to PythonAnywhere, e.g. to `/home/<username>/clinic`

2. **Create virtualenv on PythonAnywhere**

```bash
mkvirtualenv --python=python3.10 clinic-venv
pip install -r /home/<username>/clinic/requirements.txt
```

3. **Configure Web app**
   - Go to **Web** tab → "Add a new web app"
   - Choose **Manual configuration**, Python 3.x
   - Set **Source code** to: `/home/<username>/clinic`
   - Set **Working directory** to: `/home/<username>/clinic/clinic`

4. **WSGI configuration**
   - Open the WSGI file PythonAnywhere gives you (e.g. `/var/www/<username>_pythonanywhere_com_wsgi.py`)
   - Replace the Django section with:

```python
import os
import sys

path = '/home/<username>/clinic'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. **Set DJANGO_SETTINGS_MODULE (if needed)**
   - In the **Web** tab → Environment variables:
     - `DJANGO_SETTINGS_MODULE = clinic.settings`

6. **Migrate & create superuser on PythonAnywhere**

```bash
cd /home/<username>/clinic/clinic
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

7. **Static files config**
   - In **Web** tab → Static files:
     - URL: `/static/` → Directory: `/home/<username>/clinic/clinic/staticfiles`
   - Click **Reload** web app.

Your site should now be live on `https://<username>.pythonanywhere.com`.

---

## 3. Important Paths

- Django project root: `clinic/`
- App: `clinic/core/`
- Templates: `clinic/templates/`
- Static (custom CSS, etc.): `clinic/static/`

You can customize colors, fonts, and animations in:

- `clinic/static/css/style.css`


