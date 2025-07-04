🍽️ Calorie Tracker Backend API

This repository contains the backend API for a Calorie Tracker application, built with Django and Django REST Framework. It provides robust user management, food logging, and nutritional tracking.
✨ Features
👤 Users Application

    User Registration: Secure account creation with email verification.
    Email Verification: Activate accounts via emailed links.
    User Authentication: Secure login with JWT (JSON Web Tokens).
    Token Refresh & Verification: Renew and verify tokens.
    User Profile Management: Retrieve/update user profiles.
    Password Management:
        Change password
        Request password reset via email
        Confirm reset with token
    User Logout: Invalidate refresh tokens.
    Account Deletion: Users can delete their own accounts.

🍎 FoodTracker Application

    Food Search: Search food items & get nutrition from Open Food Facts API.
    Food Logging: Create food logs, auto-calculate macros/calories.
    Food Log Management: Retrieve, update, delete food logs.
    Daily Nutritional Summary: Get daily total macros/calories.

🚀 Technologies Used

    Backend: Django 5.2.4
    API: Django REST Framework 3.15
    Auth: Simple JWT 5.3
    Env Vars: python-decouple
    Docs: drf-yasg (Swagger UI / ReDoc)
    External API: Open Food Facts
    CORS: django-cors-headers
    Database: SQLite (dev), PostgreSQL (prod)

⚙️ Setup & Installation
Prerequisites

    Python 3.10+
    pip
    git

1. Clone the Repository
bash

git clone https://github.com/hazalkoom/Food-Tracker.git
cd Food-Tracker

2. Create and Activate a Virtual Environment
bash

python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

3. Install Dependencies
bash

pip install -r requirements.txt

4. Set Up Environment Variables

Create a .env file in the root:
<details> <summary>Sample <code>.env</code></summary>
env

DJANGO_SECRET_KEY='your_very_long_and_random_django_secret_key_here'
EMAIL_HOST_USER='your_gmail_email@gmail.com'
EMAIL_HOST_PASSWORD='your_gmail_app_password'
JWT_SIGNING_KEY='your_super_secret_jwt_signing_key_here'

DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOW_ALL_ORIGINS=True

</details>

    Generate Django secret:
    python -c "import secrets; print(secrets.token_urlsafe(50))"
    Gmail App Password: How to generate app password?
    JWT Signing Key:
    python -c "import secrets; print(secrets.token_urlsafe(60))"

5. Run Database Migrations
bash

python foods/manage.py makemigrations
python foods/manage.py migrate

6. Create a Superuser
bash

python foods/manage.py createsuperuser

7. Configure Django Sites

    Run server: python foods/manage.py runserver
    Go to 127.0.0.1:8000/admin/
    Update Sites domain to 127.0.0.1:8000

8. Run the Development Server
bash

python foods/manage.py runserver

API available at http://127.0.0.1:8000/api/
🗺️ API Endpoints
Authentication & User Management /api/auth/ & /api/users/
Method	Endpoint	Description	Auth?
POST	/api/auth/login/	Login (get JWT tokens)	No
POST	/api/auth/login/refresh/	Refresh access token	No
POST	/api/auth/login/verify/	Verify JWT token	No
POST	/api/users/register/	Register user	No
GET	/api/users/verify-email/<uidb64>/<token>/	Verify email	No
POST	/api/users/resend-verification/	Resend verification link	No
POST	/api/users/password-reset/	Request reset link	No
POST	/api/users/password-reset-confirm/<uidb64>/<token>/	Confirm reset	No
GET	/api/users/profile/	Get profile	Yes
PUT/PATCH	/api/users/profile/	Update profile	Yes
POST	/api/users/profile/change-password/	Change password	Yes
POST	/api/users/logout/	Logout	Yes
DELETE	/api/users/profile/	Delete account	Yes
Food Tracking & Logging /api/foodtracker/
Method	Endpoint	Description	Auth?
GET	/api/foodtracker/search/	Search foods	Yes
GET	/api/foodtracker/logs/	List food logs	Yes
POST	/api/foodtracker/logs/	Create log entry	Yes
GET	/api/foodtracker/logs/<id>/	Get log entry	Yes
PUT/PATCH	/api/foodtracker/logs/<id>/	Update log	Yes
DELETE	/api/foodtracker/logs/<id>/	Delete log	Yes
GET	/api/foodtracker/summary/	Get daily summary	Yes
📄 API Documentation

    Swagger UI: http://127.0.0.1:8000/swagger/
    ReDoc: http://127.0.0.1:8000/redoc/

Use the "Authorize" button for JWT authentication.
🧪 Testing with Postman

    Organize requests by folders:
        Authentication, Registration, User Profile, Password Reset, Food Search, Food Logging, Daily Summary
    Postman Environment Variables:
        baseUrl: http://127.0.0.1:8000/api
        accessToken, refreshToken: (populated by script)

Automate Token Storage:
js

// Add to "Tests" tab of login request
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    if (jsonData.access && jsonData.refresh) {
        pm.environment.set("accessToken", jsonData.access);
        pm.environment.set("refreshToken", jsonData.refresh);
    }
}

Clear tokens manually after logout.
📁 Project Structure
Code

.
├── .git/
├── .gitignore
├── .env
├── venv/
├── .vscode/
└── foods/
    ├── foods/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    ├── users/
    │   ├── migrations/
    │   ├── templates/email/
    │   ├── admin.py
    │   ├── api_views.py
    │   ├── models.py
    │   ├── serializer.py
    │   └── urls.py
    ├── foodtracker/
    │   ├── migrations/
    │   ├── admin.py
    │   ├── api_views.py
    │   ├── models.py
    │   ├── serializers.py
    │   └── urls.py
    ├── manage.py
    └── requirements.txt

🔮 Future Enhancements

    Frontend web/mobile integration (React, Vue, Flutter, etc.)
    Caching of FoodItems to reduce API calls
    User-defined custom foods
    Advanced unit conversion
    Meal grouping (Breakfast, Lunch, etc.)
    Goal tracking
    More nutrient fields
    Analytics and reporting
    Deployment to cloud (Heroku, AWS, GCP)
