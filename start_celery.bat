@echo off
cd /projects/braincount
echo Starting Celery Worker...
start /B celery -A braincountBackend worker -l info
echo Starting Celery Beat...
start /B celery -A braincountBackend beat -l info
echo Celery services started in background 