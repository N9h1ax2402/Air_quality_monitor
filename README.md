# Air Quality Monitoring Backend

This is the backend for the Air Quality Monitoring System, built with Django, Django REST Framework, and WebSockets for real-time monitoring.

## Features

Real-time air quality monitoring via WebSockets

MongoDB as the database using Djongo

Historical data storage and analysis

MQTT support for IoT integration

## Installation

1. Clone the repository

git clone https://github.com/your-username/your-repo.git
cd your-repo

2. Create and activate a virtual environment

python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows

3. Install dependencies

pip install -r requirements.txt

4. Apply migrations

python manage.py makemigrations
python manage.py migrate

5. Run the development server

python manage.py runserver

## API Documentation

API endpoints are available via Django REST Framework's browsable API at:

http://127.0.0.1:8000/api/

WebSocket Integration

WebSocket server runs at:

ws://127.0.0.1:8000/ws/air-quality/