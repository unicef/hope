FROM node:13-alpine as dev

WORKDIR /code/
ADD package*.json /code/
RUN npm install
ADD . /code/

EXPOSE 3000
RUN yarn build

FROM nginx:1.12-alpine
COPY --from=dev /code/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
