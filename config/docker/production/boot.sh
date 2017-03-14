#!/bin/bash

mkdir -p /var/log/nginx/
chown -R app:app /var/log/nginx/
su - app << EOF
remote_syslog
EOF