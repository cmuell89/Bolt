FROM  phusion/passenger-full:latest
MAINTAINER Carl Mueller <carl@lightninginabot.com>

ENV APP_NAME Bolt

# use baseimage-docker’s init process
CMD ["/sbin/my_init"]

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# add app to image
RUN mkdir /home/app/${APP_NAME}
ADD . /home/app/${APP_NAME}

# Install OS level dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common
RUN add-apt-repository universe
RUN apt-get update && apt-get install -y apt-utils
RUN apt-get install -qq -y python3-dev
RUN apt-get install -qq -y libffi-dev
RUN apt-get install -qq -y \
    virtualenv libffi6 postgresql-9.5 libpq-dev libffi-dev \
    gcc libatlas-base-dev libpng-dev libfreetype6  \
    libpng-dev zlib1g-dev

# Install .deb packages
RUN /home/app/${APP_NAME}/config/docker/production/deb_install.sh

# Install openjdk as installing OracleJDK might technically be illegal.
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:openjdk-r/ppa
RUN apt-get update
RUN apt-get install --fix-missing -y -f default-jre
ENV JAVA_HOME=/usr/lib/jvm/default-java

# remove disabling of nginx and default config file
RUN rm -f /etc/service/nginx/down
RUN rm /etc/nginx/sites-enabled/default

# copy nginx configuration files to corect location
ADD ./config/docker/production/bolt_nginx.conf /etc/nginx/sites-enabled/${APP_NAME}.conf
ADD ./config/docker/production/bolt_nginx_env.conf /etc/nginx/main.d/env.conf
ADD ./config/docker/production/bolt_nginx_http_directives.conf /etc/nginx/conf.d/bolt_http.conf

# Papertrails logging
ADD ./config/docker/production/log_files.yml /etc/
ADD ./config/docker/production/logrotate_nginx.conf /etc/logrorate.d/
ADD ./config/docker/production/logrotate.conf /etc/

# create virtual env
RUN cd /home/app/${APP_NAME} &&\
    virtualenv -p python3 env

# add and run boot script
ADD ./config/docker/production/boot.sh /etc/my_init.d/boot.sh
RUN /etc/my_init.d/boot.sh

# clean up when done
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*