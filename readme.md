# 🥗 Calorie Tracker Backend API

This repository contains the backend API for a **Calorie Tracker** application, built with **Django** and **Django REST Framework**. It provides robust user management, food logging, and nutritional tracking.

---

## ✨ Features

The API provides comprehensive functionalities across two main applications:

### 👤 Users Application

- **User Registration**: Secure account creation with email verification.
- **Email Verification**: Activate accounts via emailed links.
- **User Authentication**: Secure login with JWT (JSON Web Tokens).
- **Token Refresh & Verification**: Renew and verify tokens.
- **User Profile Management**: Retrieve/update user profiles.
- **Password Management**:
  - Change password
  - Request password reset via email
  - Confirm reset with token
- **User Logout**: Invalidate refresh tokens.
- **Account Deletion**: Users can delete their own accounts.

### 🍎 FoodTracker Application

- **Food Search**: Search food items & get nutrition from Open Food Facts API.
- **Food Logging**: Create food logs, auto-calculate macros/calories.
- **Food Log Management**: Retrieve, update, delete food logs.
- **Daily Nutritional Summary**: Get daily total macros/calories.

---

## 🚀 Technologies Used

- **Backend**: Django 5.2.4  
- **API**: Django REST Framework 3.15  
- **Auth**: Simple JWT 5.3  
- **Env Vars**: python-decouple  
- **Docs**: drf-yasg (Swagger UI / ReDoc)  
- **External API**: Open Food Facts  
- **CORS**: django-cors-headers  
- **Database**: SQLite (dev), PostgreSQL (prod)  

---

## ⚙️ Setup & Installation

<details>
<summary><strong>1. Clone the Repository</strong></summary>

```bash
git clone https://github.com/hazalkoom/Food-Tracker.git
cd Food-Tracker
```
</details>

<details>
<summary><strong>2. Create and Activate a Virtual Environment</strong></summary>

```bash
python -m venv venv

# On Windows:
.env\Scriptsctivate

# On macOS/Linux:
source venv/bin/activate
```
</details>

<details>
<summary><strong>3. Install Dependencies</strong></summary>

```bash
pip install -r requirements.txt
```
</details>

<details>
<summary><strong>4. Set Up Environment Variables</strong></summary>

Create a `.env` file in the root directory:

```dotenv
DJANGO_SECRET_KEY='your_very_long_and_random_django_secret_key_here'
EMAIL_HOST_USER='your_gmail_email@gmail.com'
EMAIL_HOST_PASSWORD='your_gmail_app_password'
JWT_SIGNING_KEY='your_super_secret_jwt_signing_key_here'

DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOW_ALL_ORIGINS=True
```
</details>

<details>
<summary><strong>5. Run Database Migrations</strong></summary>

```bash
python foods/manage.py makemigrations
python foods/manage.py migrate
```
</details>

<details>
<summary><strong>6. Create a Superuser</strong></summary>

```bash
python foods/manage.py createsuperuser
```
</details>

<details>
<summary><strong>7. Configure Django Sites</strong></summary>

- Run the server: `python foods/manage.py runserver`
- Visit [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- Log in → Sites → Edit → Change domain to `127.0.0.1:8000`
</details>

<details>
<summary><strong>8. Run the Development Server</strong></summary>

```bash
python foods/manage.py runserver
```
</details>

---

## 🗺️ API Endpoints

All API endpoints are prefixed with `/api/`.

### 🔐 Authentication & User Management

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | /api/auth/login/ | Obtain JWT access and refresh tokens. | Public |
| POST | /api/auth/login/refresh/ | Refresh access token. | Public |
| POST | /api/auth/login/verify/ | Verify a token. | Public |
| POST | /api/users/register/ | Register new user. | Public |
| GET | /api/users/verify-email/<uidb64>/<token>/ | Email verification. | Public |
| POST | /api/users/resend-verification/ | Resend verification email. | Public |
| POST | /api/users/password-reset/ | Request password reset. | Public |
| POST | /api/users/password-reset-confirm/<uidb64>/<token>/ | Confirm reset. | Public |
| GET | /api/users/profile/ | Get user profile. | Authenticated |
| PUT/PATCH | /api/users/profile/ | Update profile. | Authenticated |
| POST | /api/users/profile/change-password/ | Change password. | Authenticated |
| POST | /api/users/logout/ | Logout user. | Authenticated |
| DELETE | /api/users/profile/ | Delete account. | Authenticated |

### 🍽️ Food Tracking

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | /api/foodtracker/search/ | Search food items. | Authenticated |
| GET | /api/foodtracker/logs/ | List food logs. | Authenticated |
| POST | /api/foodtracker/logs/ | Create food log. | Authenticated |
| GET | /api/foodtracker/logs/<id>/ | Get food log. | Authenticated |
| PUT/PATCH | /api/foodtracker/logs/<id>/ | Update food log. | Authenticated |
| DELETE | /api/foodtracker/logs/<id>/ | Delete food log. | Authenticated |
| GET | /api/foodtracker/summary/ | Daily nutritional summary. | Authenticated |

---

## 📄 API Documentation (Swagger UI)

- Swagger UI: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)  
- ReDoc: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

---

## 🧪 Postman Testing

Organize Postman like this:

- **Authentication**: login, refresh, verify
- **Users**: register, verify, profile, logout, password reset
- **FoodTracker**: search, logs, summary

Use scripting to auto-save tokens:

```js
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    if (jsonData.access && jsonData.refresh) {
        pm.environment.set("accessToken", jsonData.access);
        pm.environment.set("refreshToken", jsonData.refresh);
    }
}
```

---

## 📁 Project Structure

```
.
├── .env
├── venv/
├── foods/
│   ├── foods/
│   ├── users/
│   └── foodtracker/
└── requirements.txt
```

---

## 🔮 Future Enhancements

- Frontend Integration
- Cached FoodItem search
- Custom user-created foods
- Meal grouping
- Goal tracking
- Micronutrient expansion
- Reporting & charts
- Cloud deployment

---

