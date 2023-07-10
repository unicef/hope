FROM cypress/included:12.4.1

WORKDIR /code

RUN apt update && apt install -y \
    curl \
    zip 

RUN curl -o /usr/local/bin/waitforit -sSL https://github.com/maxcnunes/waitforit/releases/download/v2.4.1/waitforit-linux_amd64 && \
    chmod +x /usr/local/bin/waitforit

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .
COPY docker-entrypoint.sh /usr/local/bin

ENTRYPOINT [ "docker-entrypoint.sh" ]
