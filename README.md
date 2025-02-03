# Django Kanban Board

A modern and feature-rich Kanban board application built with Django, featuring team collaboration, user management, and real-time notifications.

## Features

- 🎯 Kanban Board with customizable columns (TO DO, DOING, DONE, REJECTED)
- 👥 User Authentication and Authorization
- 🤝 Team Collaboration
- 📊 User Statistics and Analytics
- 🌓 Light/Dark Theme Support
- 📧 In-app and Email Notifications
- 👤 User Profiles with Avatars
- ⚙️ User Settings
- 📱 Responsive Design

## Tech Stack

- Backend: Django 5.0
- Database: SQLite
- Frontend: HTML5, CSS3, JavaScript
- UI Framework: Bootstrap 5
- Authentication: django-allauth
- Forms: django-crispy-forms
- Notifications: django-notifications-hq

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd Django-Kanban
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 to access the application.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 