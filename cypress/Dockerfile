FROM node:18

WORKDIR /app

RUN apt update \
    && apt install -y \
    xvfb libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libgtk-3-0 libgbm1 libasound2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -o /usr/local/bin/waitforit -sSL https://github.com/maxcnunes/waitforit/releases/download/v2.4.1/waitforit-linux_amd64 && \
    chmod +x /usr/local/bin/waitforit

COPY package*.json ./
COPY yarn.lock ./
RUN yarn install

COPY . .

ENTRYPOINT [ "./docker-entrypoint.sh" ]


