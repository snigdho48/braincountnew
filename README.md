# BrainCount Backend

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

### Setting up Celery Services

1. Copy the service files to systemd:
```bash
sudo cp celery-worker.service /etc/systemd/system/
sudo cp celery-beat.service /etc/systemd/system/
```

2. Update the service files with your actual paths:
   - Replace `/path/to/braincountBackend` with your actual project path
   - Update user/group if needed (default is www-data)

3. Reload systemd:
```bash
sudo systemctl daemon-reload
```

4. Enable services to start on boot:
```bash
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat
```

5. Start the services:
```bash
sudo systemctl start celery-worker
sudo systemctl start celery-beat
```

### Checking Service Status

To check if services are running:
```bash
sudo systemctl status celery-worker
sudo systemctl status celery-beat
sudo systemctl status redis
```

To view logs:
```bash
journalctl -u celery-worker
journalctl -u celery-beat
journalctl -u redis
```

### Service Files

#### celery-worker.service
```ini
[Unit]
Description=Celery Worker Service
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/braincountBackend
Environment="PATH=/path/to/braincountBackend/venv/bin"
ExecStart=/path/to/braincountBackend/venv/bin/python manage.py celery worker -l info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### celery-beat.service
```ini
[Unit]
Description=Celery Beat Service
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/braincountBackend
Environment="PATH=/path/to/braincountBackend/venv/bin"
ExecStart=/path/to/braincountBackend/venv/bin/python manage.py celery beat -l info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
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