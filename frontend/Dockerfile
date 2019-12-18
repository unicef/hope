FROM node:13-alpine as dev

ARG ssh_prv_key
ARG ssh_pub_key

WORKDIR /code/
RUN apk add --no-cache openssh git
ADD package*.json /code/
# Authorize SSH Host
RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan github.com > /root/.ssh/known_hosts

RUN echo "$ssh_prv_key" > /root/.ssh/id_rsa && \
    echo "$ssh_pub_key" > /root/.ssh/id_rsa.pub && \
    chmod 600 /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa.pub
RUN npm install
ADD . /code/

EXPOSE 3000
RUN yarn build

FROM nginx:1.12-alpine
COPY --from=dev /code/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]