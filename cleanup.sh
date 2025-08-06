cd /home/pi/website
source website_env/bin/activate
python3 cleanup_sessions.py >> /home/pi/website/logs/cleanups.log
