#!/bin/bash

mkdir -p /run/nginx/

doconfig(){
    sed "s:FLOWER_URL_PREFIX:${FLOWER_URL_PREFIX}:g" $TEMPLATE > /conf/nginx.conf
    sed -i "s:SERVER_NAME:${SERVER_NAME}:g" /conf/nginx.conf
    sed -i "s:SERVER_PORT:${SERVER_PORT}:g" /conf/nginx.conf
    sed -i "s:FLOWER_ADDRESS:${FLOWER_ADDRESS}:g" /conf/nginx.conf
}

TEMPLATE='/conf/nginx.conf.tpl'

if [ "$*" == "config" ]; then
  doconfig
  cat /conf/nginx.conf
elif [ "$*" == "start" ]; then
    echo "Starting NGINX on port ${SERVER_PORT}"
    echo "Starting Flower ${FLOWER_ADDRESS}"
    doconfig
    flower --version
    flower auto_refresh=false &
    nginx -c /conf/nginx.conf
else
    exec "$@"
fi
