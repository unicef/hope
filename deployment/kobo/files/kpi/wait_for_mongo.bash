#!/bin/bash
set -e

echo 'Waiting for container `mongo`.'
wait-for-it -t 40 -h ${KPI_MONGO_HOST} -p ${KPI_MONGO_PORT}
echo 'Container `mongo` up.'}
