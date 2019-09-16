FROM node:12.10.0-buster

RUN echo "deb http://nginx.org/packages/debian/ buster nginx" >> /etc/apt/sources.list.d/nginx.list
RUN apt-key adv --fetch-keys "http://nginx.org/keys/nginx_signing.key"

RUN apt-get update
RUN apt-get -y install nginx
RUN rm -rf /etc/nginx/conf.d/*
RUN mkdir -p /srv/www/

ADD nginx.conf /etc/nginx/nginx.conf
ADD nginx_site.conf /etc/nginx/conf.d/default.conf

ADD entrypoint.sh /
ADD compile-production.sh /

RUN chmod +x entrypoint.sh
RUN chmod +x compile-production.sh

ADD package.json yarn.lock /tmp/
RUN cd /tmp && yarn install

ADD . /code/
RUN rm -rf /code/node_modules
RUN cp -a /tmp/node_modules /code/node_modules

WORKDIR /code

EXPOSE 8080
CMD ["yarn run start"]
