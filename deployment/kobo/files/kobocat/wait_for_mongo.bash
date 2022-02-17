#!/bin/bash
set -e

echo 'Waiting for container `mongo`.'
wait-for-it -t 40 -h ${KOBOCAT_MONGO_HOST} -p ${KOBOCAT_MONGO_PORT}
echo 'Container `mongo` up.'}