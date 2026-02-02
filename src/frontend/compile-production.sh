#!/bin/sh

cd /code
bun run build
cp -r build/* /srv/www/
