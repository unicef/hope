#!/bin/sh

/./compile-production.sh
nginx -g "daemon off;"
