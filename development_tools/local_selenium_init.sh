if [ "$0" = "$BASH_SOURCE" ]; then
    echo "Please source this script."
    exit 1
fi
export SECRET_KEY=SOME_KEY_HERE
export DEBUG=true
export ENV=dev
export POSTGRES_DB=postgres
export POSTGRES_USER=postgres
export POSTGRES_PASS=postgres
export PGUSER=postgres
export POSTGRES_HOST_AUTH_METHOD=trust
export DATABASE_URL=postgis://postgres:postgres@localhost:5432/postgres
export POSTGRES_SSL_MODE=off
export EMAIL_HOST=TBD
export EMAIL_HOST_USER=TBD
export EMAIL_HOST_PASSWORD=TBD
export MAP_BOX_KEY=MAP_BOX_KEY_HERE
export SOCIAL_AUTH_REDIRECT_IS_HTTPS=false
export AZURE_CLIENT_ID=
export AZURE_CLIENT_SECRET=
export AZURE_TENANT_KEY=
export STORAGE_AZURE_ACCOUNT_KEY=
export STORAGE_AZURE_ACCOUNT_NAME=
export KOBO_API_URL=https://kobo.humanitarianresponse.info
export KOBO_KF_URL=https://kobo.humanitarianresponse.info
export KOBO_KC_URL=https://kobo.humanitarianresponse.info
export ADMIN_PANEL_URL=unicorn
export PROFILING=off
export CYPRESS_TESTING=yes
export DJANGO_ALLOWED_HOST=localhost
export HCT_MIS_FRONTEND_HOST=localhost:8080
export REDIS_INSTANCE=localhost:6379
export PYTHONUNBUFFERED=1
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/0
export CACHE_LOCATION=redis://localhost:6379/1
export USE_DUMMY_EXCHANGE_RATES=yes
export ELASTICSEARCH_HOST=http://localhost:9200
export CELERY_TASK_ALWAYS_EAGER=true
# export LIBRARY_PATHS=true
SCRIPT_DIR=$(realpath "$(dirname $0)")
MAIN_DIR=$(realpath $SCRIPT_DIR/..)
echo "SCRIPT_DIR: $SCRIPT_DIR"
export PYTHONPATH=$MAIN_DIR/src:$PYTHONPATH
export OUTPUT_DATA_ROOT=$MAIN_DIR/tests/selenium/output_data
export DATA_VOLUME=$OUTPUT_DATA_ROOT/data
pushd  $MAIN_DIR/src/frontend
yarn
yarn build-for-backend
popd
