#!/bin/sh

cd /code
yarn run build
cp -r build/* /srv/www/
