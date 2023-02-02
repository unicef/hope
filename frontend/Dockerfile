FROM node:13-alpine as dev

WORKDIR /code/
ADD yarn.lock package.json /code/
RUN yarn install
ADD . /code/

ARG SENTRY_FRONTEND_DSN
ENV SENTRY_FRONTEND_DSN=${SENTRY_FRONTEND_DSN}
EXPOSE 3000

CMD ["yarn", "start"]

FROM node:13-alpine as dist-builder
RUN yarn build

FROM nginx:1.12-alpine as dist
COPY --from=dist-builder /code/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
