USERNAME=$(cat /mnt/secrets/username)
AUTH_TOKEN=$(cat /mnt/secrets/token)

cd /home/pi/website

git pull https://$USERNAME:$AUTH_TOKEN@github.com/SnekByte-Studios/website.git
source website_env/bin/activate
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
