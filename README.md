Air Quality Monitoring Backend

This is the backend for the Air Quality Monitoring System, built with Django, Django REST Framework, and WebSockets for real-time monitoring.

Features

User authentication using JWT

Real-time air quality monitoring via WebSockets

MongoDB as the database using Djongo

Historical data storage and analysis

MQTT support for IoT integration

Background tasks with Celery & Redis

Installation

Prerequisites

Make sure you have the following installed:

Python (>=3.8)

MongoDB

Redis (for Celery background tasks)

1. Clone the repository

git clone https://github.com/your-username/your-repo.git
cd your-repo

2. Create and activate a virtual environment

python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows

3. Install dependencies

pip install -r requirements.txt

If you haven't created requirements.txt, run:

pip install django pymongo djongo djangorestframework djangorestframework-simplejwt channels
pip freeze > requirements.txt

4. Configure .env file

Create a .env file and add your environment variables:

DJANGO_SECRET_KEY=your-secret-key
MONGODB_URI=mongodb://localhost:27017/your-db-name
DEBUG=True

5. Apply migrations

python manage.py makemigrations
python manage.py migrate

6. Run the development server

python manage.py runserver

7. Start Celery (for background tasks)

celery -A air_quality_monitor worker --loglevel=info

API Documentation

API endpoints are available via Django REST Framework's browsable API at:

http://127.0.0.1:8000/api/

WebSocket Integration

WebSocket server runs at: