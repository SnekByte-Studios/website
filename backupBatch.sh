#!/bin/bash

PASSWORD=$(cat /mnt/password)
AUTH_TOKEN=$(cat /mnt/token)
USERNAME=$(cat /mnt/username)

cp /home/pi/website/*.sqlite3 /home/pi/website_backup/
cp /home/pi/website/*.crt /home/pi/website_backup/
cp /home/pi/website/*.key /home/pi/website_backup/
cp /home/pi/website/*.pem /home/pi/website_backup/
cp -r /home/pi/website/logs /home/pi/website_backup/
cd /home/pi/website

git add .
git commit -m "Backup changes: $(date)"
git push https://$USERNAME:$AUTH_TOKEN@github.com/SnekByte-Studios/website_backup.git
echo "Backup and push completed successfully!"
