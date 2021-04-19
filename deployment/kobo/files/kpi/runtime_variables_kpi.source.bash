if [[ ! -z "${PUBLIC_DOMAIN_NAME}" ]]; then
    if [[ ${NGINX_PUBLIC_PORT} != "" && ${NGINX_PUBLIC_PORT} != "80" ]]; then
        PUBLIC_PORT=":${NGINX_PUBLIC_PORT}"
    else
        PUBLIC_PORT=""
    fi
    export SESSION_COOKIE_DOMAIN=".${PUBLIC_DOMAIN_NAME}"
    export DJANGO_ALLOWED_HOSTS=".${PUBLIC_DOMAIN_NAME} .${INTERNAL_DOMAIN_NAME} kubernetes.internal"

    export KPI_DATABASE_URL="postgis://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${KPI_POSTGRES_DB}"
    export KC_DATABASE_URL="postgis://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${KOBOCAT_POSTGRES_DB}"
    export KPI_BROKER_URL="redis://:${REDIS_PASSWORD}@redis-main-master:6379/1"
    export REDIS_SESSION_URL="redis://:${REDIS_PASSWORD}@redis-main-master:6379/2"

    # DATABASE
    export DATABASE_URL="${KPI_DATABASE_URL}"
    export POSTGRES_DB="${KPI_POSTGRES_DB}"

    # OTHER
    export RAVEN_DSN="${KPI_RAVEN_DSN}"
    export RAVEN_JS_DSN="${KPI_RAVEN_JS_DSN}"
    export KPI_URL="${KOBOFORM_URL}"
else
    echo 'Please fill out your `envfile`!'
    exit 1
fi
