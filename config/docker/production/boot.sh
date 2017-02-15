#!/bin/sh

dir="/home/app/bolt"
logfile="/var/log/bolt.log"

touch "$logfile"
chown -R app:app "$logfile"

mkdir -p /var/log/nginx/
chown -R www-data:adm /var/log/nginx/

#su - app <<EOF
#cd /home/app/bolt
#source env/bin/activate
#pip install -r requirements.txt
#deactivate
#EOF

chown -R app:app "$dir"
source /etc/environment