FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-alpine3.10 as base

FROM base as builder

WORKDIR /app/

RUN apk update && \
    apk add --no-cache \
python3-dev autoconf automake  snappy-dev g++ make  \
      libffi libffi-dev  libxml2-dev  libxslt-dev libressl-dev ca-certificates curl bash gcc musl-dev mariadb-connector-c-dev && \
    apk upgrade busybox expat 

RUN apk add cyrus-sasl cyrus-sasl-crammd5 cyrus-sasl-digestmd5 cyrus-sasl-login cyrus-sasl-ntlm postfix
RUN apk add cyrus-sasl openldap-dev snappy-dev

RUN apk add gcc git libressl-dev g++ make && \
  cd /tmp && git clone https://github.com/edenhill/librdkafka.git && \
  cd librdkafka && git checkout tags/v2.0.2 && \
  ./configure --enable-ssl --enable-gssapi && make && make install && \
  #./configure && make && make install && \
  cd ../ && rm -rf librdkafka


# Install Poetry
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "cryptography==3.3.2" poetry pipenv && \
    poetry config virtualenvs.create false

# Upgrade urllib3
RUN pip install --no-cache-dir --upgrade urllib3
RUN pip install PyMySQL
RUN pip install httpcore==0.15

# Copies dependencies definition
COPY ./app/pyproject.toml /app/
COPY ./app/requirements.txt /app/
#COPY ./app/poetry.lock /app/
RUN pip install -r requirements.txt --index-url https://gitlab.tinaa.teluslabs.net/api/v4/projects/1029/packages/pypi/simple --trusted-host gitlab.tinaa.teluslabs.net

# SSL
RUN echo -e "-----BEGIN CERTIFICATE-----\n\
MIIFCzCCAvOgAwIBAgIQPV3nXivRnLxDck9T/xzOFDANBgkqhkiG9w0BAQsFADAX\n\
MRUwEwYDVQQDEwxUQ1NPLXJvb3QtQ0EwIBcNMjAwMzEwMTgzNDA5WhgPMjA1MDAz\n\
MTAxODQ0MDZaMBcxFTATBgNVBAMTDFRDU08tcm9vdC1DQTCCAiIwDQYJKoZIhvcN\n\
AQEBBQADggIPADCCAgoCggIBAO4/pqgs8bnjKYk/2CTbL1Po/SvqQxSkl7NGARiK\n\
xT6Qgm8DwN8BXkwwy1yrRA8v3DJ24aBsZ9Z6uw6wYSdIdMyczTS3bOLf1SrATjy5\n\
kkYuvi8jsU875xIc3WPVNZNB0hzBSnYQslYg93yTk0K7D3h7KZauKqDzS0Sv4R7X\n\
LPxz2pqSYEsWYklKfhPP5B426lnuepH8VrCf+dV13AINXC8GcHlEf/nDviPBEc8M\n\
NrgjhLBpSHapeTAlfuUGtzFmHnZhGhTKAUgyX2tBxrhuLyXeqRuItDoPQGZirf2R\n\
owrZQ418WRNNv4lQn4H/geuitMEbcaxaXf+EI+/PfibV++KsDG0RZdQiP6tPs7vL\n\
f5IqLX9B0ip4GuGAFxU+TdZ9H/qxkJeoA84heDEzt6DD7fXkpS4NYBLf2zwgXBay\n\
iIeUjxIdT3ZPu482eX+fdwMbjg3CFr8IMMsvzJN44c7ElUpW+BUzu/Ri4E/UpXUf\n\
nxNnGAsZ3l/dih1VaJKOITCmRVbWQTPaK6F5Ey5tB0tcx+LzyBM9hbr51Wkfq2M+\n\
ZDErcEavsBrDVHi1eLFMvWIsNk6B1ERvzqDFBiq86BKhwVXFABb5sT5CVQK1JK84\n\
I0XbNh8UVNhWPc3VqazBlMeuYhFypQioNoW/FNPulr5Tc6tSycC/8tOsC2Y7sOd6\n\
bpL5AgMBAAGjUTBPMAsGA1UdDwQEAwIBhjAPBgNVHRMBAf8EBTADAQH/MB0GA1Ud\n\
DgQWBBT9uhYG4VsJyfnPrjEWvxBNf8CQUzAQBgkrBgEEAYI3FQEEAwIBADANBgkq\n\
hkiG9w0BAQsFAAOCAgEAhDYABqRsidmAbVHlpjdRBTN5rzS1pUD6jh5gfr6aiVGH\n\
ejzCRMyeGPRsKmhDH9zxJ+LCeiXZyk59DcMXZUlUE6YLRuLFCqkhKsgFqMeUH/iJ\n\
7jxcFZ/QjyeB7TQsaaGMzi3JxwKaKkwwYhmjqF+8BZlyhaPIfbaGxOYWvJ4zBM2L\n\
L+0w8wnCm8sfIx7KSaB+Pae4sP6x0i8x/jJbA4iB3CTrU2QE1iO8B1Np1HUq5ili\n\
3QdBJrvL4WLRFrVkIhpNdRU4DsHPaEPmXAxJjF7KvAVVw6Own+ftMGnoml3MzSBq\n\
0wQkWpZLkLUTjWAGCO/wdkW3oVkPoeqTziLlB8LzYVPIT/rC/HkFO4WHld5YXs/H\n\
ErQIFbKUUr9452jy+KaTHUnli30bRjZPEapv7JKGg6dL1d+VOxMuQFSPKUcss3uo\n\
L+uIxt9Ot5kiqQFuzGy4rNveMVgmuwBQg9RchIWAxBImq/+akDqMJomEYHDFRZCj\n\
fIV16cASS9ABWc1CNndmJh3m11hVTm+5T0Ags9ubj8GAIr4EsNXrKEpOXxsnOeBp\n\
v6BQOTe/g724yMazG06Tdpj058aaBqSdeRaKxPoYMXmdj/e28RmpO9jE1+sE/aJZ\n\
wNlbilaf3Boaq2c3AODbJBn96fkwshnRuxB6eL84bbB1xD5VmAXDztCMmFMBrPA=\n\
-----END CERTIFICATE-----" >> /etc/ssl/cert.pem

ENV REQUESTS_CA_BUNDLE=/etc/ssl/cert.pem

RUN pip install --upgrade pip setuptools wheel

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN sh -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --without dev ; fi"

#RUN pip uninstall --yes poetry

FROM builder
ARG $ROUTE_CACERTIFICATE
WORKDIR /app/
ENV PYTHONPATH=/app
ENV REQUESTS_CA_BUNDLE=/etc/ssl/cert.pem
COPY --from=builder /usr/local /usr/local
RUN true                                  # because of https://github.com/moby/moby/issues/37965
COPY --from=builder /etc/ssl/cert.pem /etc/ssl/cert.pem
COPY ./app /app
COPY ./telus_tcso_ca.pem.txt /
