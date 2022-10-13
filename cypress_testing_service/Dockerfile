FROM node:16.14-bullseye-slim

WORKDIR /code

RUN apt update \
    && DEBIAN_FRONTEND=noninteractive apt install --no-install-recommends -y \
    curl ca-certificates npm \
    libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb \
    && apt clean && rm -rf /var/lib/apt/lists/*

COPY package*.json yarn.lock ./
RUN yarn --pure-lockfile

RUN yarn global add wait-on

ADD . /code/

CMD ["./docker-entrypoint.sh"]