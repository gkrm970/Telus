FROM python:3.8.12-alpine3.14
ARG TCSO_ROOT_CA

RUN echo "$TCSO_ROOT_CA" > /usr/local/share/ca-certificates/tcso-root.crt

RUN mv /usr/local/share/ca-certificates/*.crt /usr/local/share/ca-certificates/*.crt && update-ca-certificates
ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt
RUN apk -U upgrade

RUN apk update && apk add bash

RUN apk add cyrus-sasl cyrus-sasl-crammd5 cyrus-sasl-digestmd5 cyrus-sasl-login cyrus-sasl-ntlm postfix
RUN apk add cyrus-sasl openldap-dev snappy-dev libffi-dev

RUN apk add gcc git libressl-dev g++ make && \
  cd /tmp && git clone https://github.com/edenhill/librdkafka.git && \
  cd librdkafka && git checkout tags/v2.0.2 && \
  ./configure --enable-ssl --enable-gssapi && make && make install && \
  #./configure && make && make install && \
  cd ../ && rm -rf librdkafka

RUN apk add build-base

COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN python3.8 -m pip install setuptools

RUN python3.8 -m pip install -r requirements.txt  --index-url https://gitlab.tinaa.teluslabs.net/api/v4/projects/1029/packages/pypi/simple --trusted-host gitlab.tinaa.teluslabs.net

# update-ca-certificates command not working. Hence reseting REQUESTS_CA_BUNDLE to work with TCSO
ENV REQUESTS_CA_BUNDLE /usr/local/share/ca-certificates/tcso-root.crt

COPY . /

ENTRYPOINT ["python3.8", "discovery_service_wrapper.py"]
