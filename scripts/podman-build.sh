#! /usr/bin/env sh

# Exit in case of error
set -e


export DOMAIN=backend
export SMTP_HOST=""
export TRAEFIK_PUBLIC_NETWORK_IS_EXTERNAL=false
export INSTALL_DEV=true

podman-compose -f docker-compose.yml build
