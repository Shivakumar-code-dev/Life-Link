# 🩸 LifeFlow — Smart Blood Donation Registry Portal

A full-stack Flask + Firebase web application for managing blood donors, emergency requests, and hospital blood registry operations.

---

## 📁 Project Structure

```
blood_donation_portal/
├── app.py                    # Flask app — all routes & business logic
├── firebase_config.py        # Firebase Admin SDK initialization
├── requirements.txt          # Python dependencies
├── serviceAccountKey.json    # ← YOU MUST ADD THIS (Firebase key)
├── .env.example              # Environment variable template
├── templates/
│   ├── base.html             # Master layout (nav, footer, flash messages)
│   ├── index.html            # Landing page
│   ├── donor_register.html   # Donor registration form
│   ├── donor_login.html      # Donor login
│   ├── donor_dashboard.html  # Donor dashboard (profile, history, requests)
│   ├── search_donor.html     # Search donors by blood group & city
│   ├── request_blood.html    # Emergency blood request form
│   ├── admin_login.html      # Admin login
│   ├── admin_dashboard.html  # Admin panel (approve/reject/manage)
│   └── admin_setup.html      # One-time admin account creation
└── static/
    ├── css/style.css         # Full responsive stylesheet
    └── js/script.js          # Frontend interactivity
```

---

## 🚀 Setup Instructions (VS Code)

### Step 1 — Clone / Open the Project
Open the `blood_donation_portal/` folder in VS Code.

### Step 2 — Create a Virtual Environment
```bash
# In VS Code terminal (Ctrl + `)
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Set Up Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project (or use existing)
3. Enable **Firestore Database** in Native mode
4. Go to **Project Settings → Service Accounts**
5. Click **"Generate new private key"** → download JSON
6. Rename the file to `serviceAccountKey.json`
7. Place it in the `blood_donation_portal/` root folder

### Step 5 — Configure Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env and set:
SECRET_KEY=your-random-secret-key-here
FIREBASE_SERVICE_ACCOUNT=serviceAccountKey.json
```

### Step 6 — Run the Application
```bash
python app.py
```

Visit: **http://127.0.0.1:5000**

---

## 🔐 First-Time Admin Setup

1. Visit: `http://127.0.0.1:5000/admin/setup`
2. Create your admin account (name, email, password)
3. This page auto-disables once an admin exists
4. Login at: `http://127.0.0.1:5000/admin/login`

---

## 🔥 Firebase Firestore Collections

| Collection         | Description                            |
|--------------------|----------------------------------------|
| `donors`           | All donor registrations                |
| `blood_requests`   | Emergency blood requests               |
| `donation_history` | Logged donations per donor             |
| `admins`           | Admin accounts (hashed passwords)      |

### Donor Document Structure
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91 98765 43210",
  "blood_group": "A+",
  "city": "Mumbai",
  "address": "123 Main Street",
  "age": 28,
  "last_donation_date": "2024-11-15",
  "password": "<bcrypt hash>",
  "status": "pending",
  "registered_at": "2025-01-10T10:30:00"
}
```

---

## 🌐 All Routes

| Route                        | Method    | Description                    |
|------------------------------|-----------|--------------------------------|
| `/`                          | GET       | Landing page                   |
| `/register`                  | GET/POST  | Donor registration             |
| `/login`                     | GET/POST  | Donor login                    |
| `/logout`                    | GET       | Donor logout                   |
| `/dashboard`                 | GET       | Donor dashboard (protected)    |
| `/dashboard/update`          | POST      | Update donor profile           |
| `/search`                    | GET       | Search donors                  |
| `/request-blood`             | GET/POST  | Post emergency request         |
| `/admin/login`               | GET/POST  | Admin login                    |
| `/admin/logout`              | GET       | Admin logout                   |
| `/admin/dashboard`           | GET       | Admin panel (protected)        |
| `/admin/donor/<id>/approve`  | GET       | Approve a donor                |
| `/admin/donor/<id>/reject`   | GET       | Reject a donor                 |
| `/admin/donor/<id>/delete`   | GET       | Delete a donor                 |
| `/admin/request/<id>/close`  | GET       | Close a blood request          |
| `/admin/setup`               | GET/POST  | One-time admin setup           |

---

## 🔒 Security Features

- Passwords hashed with **Werkzeug** (bcrypt)
- Session-based authentication
- Admin routes protected with `@admin_login_required`
- Donor routes protected with `@donor_login_required`
- Donor status must be `approved` to log in
- Admin setup page auto-disables after first admin creation

---

## 💡 VS Code Tips

- Install the **Python** extension for IntelliSense
- Install **Pylance** for type hints
- Use `Ctrl + \`` to open the integrated terminal
- Install **Jinja** extension for template syntax highlighting

---

## 📦 Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Frontend   | HTML5, CSS3, JavaScript |
| Backend    | Python 3.10+, Flask 3   |
| Database   | Firebase Firestore      |
| Auth       | Flask Sessions + Werkzeug|
| Fonts      | Google Fonts (Playfair Display + DM Sans) |

---

*Built with ❤️ to save lives.*
