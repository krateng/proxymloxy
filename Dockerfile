from python:alpine

RUN apk add --no-cache python3 nginx py3-pip

WORKDIR /usr/src/app
RUN pip install --no-dependencies doreah
COPY . .
RUN pip install .

ENTRYPOINT ["proxymloxy","-i","/etc/proxymloxy/proxymloxy.yml","--foreground_nginx","true"]
