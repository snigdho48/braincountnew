# BrainCount Backend

This is the backend for the BrainCount application, built with Django and Django REST Framework.

## Prerequisites

- Python 3.8 or higher
- Redis server
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd braincountBackend
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
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

## Running the Application

1. Start the Django development server:
```bash
python manage.py runserver
```

2. Start Redis server (required for Celery and Channels):
```bash
redis-server
```

3. Start Celery worker (in a new terminal):
```bash
celery -A braincountBackend worker -l info
```

4. Start Celery beat for periodic tasks (in a new terminal):
```bash
celery -A braincountBackend beat -l info
```

## API Documentation

The API documentation is available at:
- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

## Project Structure

```
braincountBackend/
├── api/                    # Main application code
├── braincountBackend/      # Project settings
├── media/                  # User-uploaded files
├── static/                 # Static files
├── manage.py              # Django management script
└── requirements.txt       # Project dependencies
```

## Features

- User authentication with JWT
- Campaign management
- Billboard management
- Impression tracking
- Real-time updates with WebSocket
- Periodic tasks with Celery
- API documentation with Swagger/ReDoc

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

The project follows PEP 8 style guide. You can check your code style with:

```bash
flake8
```

## Deployment

1. Set `DEBUG = False` in settings.py
2. Configure your production database
3. Set up a production web server (e.g., Gunicorn)
4. Configure static and media files
5. Set up SSL/TLS certificates
6. Configure environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]

## Support

For support, please contact [Your Contact Information]

## Background Services Setup

This project uses Redis for two main purposes:
1. Celery task queue for background tasks
2. Notification services

### Prerequisites

1. Redis Server
2. Python 3.x
3. Virtual Environment

### Installation

1. Install Redis:
```bash
sudo apt-get update
sudo apt-get install redis-server
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Redis Configuration

Redis is used for:
- Celery task queue (for impression updates)
- Notification services (real-time notifications)

Make sure Redis is running:
```bash
sudo systemctl status redis
```

If Redis is not running:
```bash
sudo systemctl start redis
```

To enable Redis on boot:
```bash
sudo systemctl enable redis
```

### Linux

1. Copy the service files to systemd directory:
```bash
sudo cp celery-worker.service /etc/systemd/system/
sudo cp celery-beat.service /etc/systemd/system/
```

2. Reload systemd:
```bash
sudo systemctl daemon-reload
```

3. Enable and start the services:
```bash
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat
sudo systemctl start celery-worker
sudo systemctl start celery-beat
```

4. Check service status:
```bash
sudo systemctl status celery-worker
sudo systemctl status celery-beat
```

5. View logs:
```bash
sudo journalctl -u celery-worker
sudo journalctl -u celery-beat
```

The services are configured to run from `/projects/braincount` directory with the following settings:
- User: root
- Group: root
- Working Directory: /projects/braincount
- Dependencies: network.target and redis.service
- Auto-restart: enabled
- Start on boot: enabled

To stop the services:
```bash
sudo systemctl stop celery-worker
sudo systemctl stop celery-beat
```

To restart the services:
```bash
sudo systemctl restart celery-worker
sudo systemctl restart celery-beat
```

### Troubleshooting

1. If services fail to start:
   - Check Redis is running: `sudo systemctl status redis`
   - Check logs: `journalctl -u celery-worker` or `journalctl -u celery-beat`
   - Verify paths in service files are correct
   - Ensure proper permissions on project directory

2. If tasks aren't running:
   - Check Celery beat schedule: `celery -A braincountBackend beat -l info`
   - Verify Redis connection
   - Check task logs in Celery worker

3. If notifications aren't working:
   - Check Redis connection: `redis-cli ping`
   - Verify Redis is running: `sudo systemctl status redis`
   - Check Redis logs: `journalctl -u redis`

### Manual Testing

To test the setup manually:

1. Start Redis:
```bash
redis-server
```

2. Start Celery worker:
```bash
python manage.py celery worker -l info
```

3. Start Celery beat:
```bash
python manage.py celery beat -l info
```

The following services should be running:
- Redis server (for both Celery and notifications)
- Celery worker (for processing tasks)
- Celery beat (for scheduling tasks)
- Notification service (for real-time notifications)

The impression update task will run every hour automatically when the services are running. 