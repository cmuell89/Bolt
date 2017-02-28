#!/bin/sh

dir="/home/app/Bolt"
logfile="/var/log/Bolt.log"

touch "$logfile"
chown -R app:app "$logfile"

mkdir -p /var/log/nginx/
chown -R www-data:adm /var/log/nginx/

chown -R app:app "$dir"
