# CyberAware – Cybersecurity Awareness Game

A Flask-based web application for cybersecurity awareness training (Project 2 – ICT932).

## Features

- **Secure Authentication** – Registration, Login with bcrypt password hashing
- **Two-Factor Authentication (2FA)** – TOTP via Google Authenticator / Authy
- **Role-Based Access Control** – Student & Teacher roles
- **15+ Challenges** across 4 categories:
  - Phishing Email Identification
  - Password Security
  - Social Engineering Awareness
  - Secure Browsing Practices
- **Scoring System** – Points per challenge with attempt penalties
- **Achievement Badges** – Awarded on milestones
- **Leaderboard** – Compare progress with classmates
- **Teacher Dashboard** – Track all student progress + audit logs
- **Audit Logging** – All actions logged with timestamps and IPs

## Tech Stack

| Layer     | Technology        |
|-----------|-------------------|
| Backend   | Python / Flask    |
| Frontend  | Tailwind CSS (CDN)|
| Database  | SQLite (via SQLAlchemy) |
| Auth      | Flask-Login + PyOTP (TOTP 2FA) |
| Passwords | Werkzeug bcrypt   |

## Setup & Installation

### 1. Clone / Extract
```bash
cd cyberaware
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
cd src
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

## Usage

1. **Register** a new account (Student or Teacher role)
2. **Scan the QR code** with Google Authenticator to set up 2FA
3. **Login** and enter the 6-digit 2FA code
4. **Complete challenges** in the Challenges section
5. **Track progress** on the Dashboard and Leaderboard
6. Teachers can access **Admin** panel for student monitoring

## Project Structure

```
cyberaware/
├── src/
│   ├── app.py          # Main Flask application
│   ├── models.py       # SQLAlchemy database models
│   ├── seed.py         # Challenge seed data (15+ challenges)
│   └── templates/      # Jinja2 HTML templates
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── setup_2fa.html
│       ├── verify_2fa.html
│       ├── dashboard.html
│       ├── challenges.html
│       ├── challenge.html
│       ├── leaderboard.html
│       └── admin.html
├── docs/               # Documentation
├── tests/              # Test files
├── ci-cd/              # CI/CD pipeline configs
├── requirements.txt
└── README.md
```

## Security Features Implemented

- Password hashing with Werkzeug (bcrypt)
- TOTP Two-Factor Authentication (RFC 6238)
- Role-Based Access Control (Student / Teacher)
- Parameterized SQL queries via SQLAlchemy ORM
- Audit logging for all user actions
- Session management via Flask-Login
- Input sanitization via Jinja2 auto-escaping

## Default Test Credentials

Register your own account. For a teacher account, select "Teacher" during registration.
