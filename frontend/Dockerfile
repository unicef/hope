FROM node:13-alpine as dev
WORKDIR /code

FROM node:13-alpine as dist-builder

WORKDIR /code

COPY package.json yarn.lock /code/

RUN --mount=type=cache,target=/root/.cache,sharing=private \
    yarn install --frozen-lockfile

COPY . /code/

RUN yarn build

FROM nginx:1.23.3-alpine as dist
COPY --from=dist-builder /code/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80

COPY docker-entrypoint.sh /bin/
ENTRYPOINT [ "docker-entrypoint.sh" ]

CMD ["nginx", "-g", "daemon off;"]
