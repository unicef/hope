FROM nginx:1.15.6-alpine

RUN apk update
RUN apk add --upgrade --no-cache py-pip bash
RUN pip install j2cli

ADD nginx.conf.j2 /
ADD nginx-site.conf.j2 /
ADD docker-entrypoint.sh /
ADD main.sh /

RUN chmod a+rx /docker-entrypoint.sh
RUN chmod a+rx /main.sh
ENTRYPOINT ["/bin/bash", "/docker-entrypoint.sh"]

EXPOSE 80
EXPOSE 443

CMD ["/main.sh"]
