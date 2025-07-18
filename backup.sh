#!/bin/bash

PASSWORD=$(cat /mnt/secrets/password)
AUTH_TOKEN=$(cat /mnt/secrets/token)
USERNAME=$(cat /mnt/secrets/username)

echo $PASSWORD
echo $AUTH_TOKEN
echo $USERNAME

cp /home/pi/website/*.sqlite3 /home/pi/website_backup/
cp /home/pi/website/*.crt /home/pi/website_backup/
cp /home/pi/website/*.key /home/pi/website_backup/
cp /home/pi/website/*.pem /home/pi/website_backup/
cp -r /home/pi/website/logs /home/pi/website_backup/
cd /home/pi/website_backup

git add .
git commit -m "Backup changes: $(date)"
git push https://$USERNAME:$AUTH_TOKEN@github.com/SnekByte-Studios/website_backup.git
echo "Backup and push completed successfully!"
