FROM node:13-alpine as dev
WORKDIR /code
COPY package.json yarn.lock /code/
RUN --mount=type=cache,target=/root/.cache,sharing=private \
    yarn install --frozen-lockfile
COPY . /code/
EXPOSE 3000
CMD ["yarn", "start"]

FROM node:13-alpine as dist-builder
WORKDIR /code
COPY --from=dev /code /code
ARG SENTRY_DSN
ENV SENTRY_DSN=$SENTRY_DSN
ARG SENTRY_ENVIRONMENT
ENV SENTRY_ENVIRONMENT=$SENTRY_ENVIRONMENT
RUN yarn build

FROM nginx:1.23.3-alpine as dist
COPY --from=dist-builder /code/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
