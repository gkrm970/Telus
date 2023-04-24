#! /usr/bin/env sh
set -e

python /app/app/tests_pre_start.py

sh ./scripts/test.sh "$@"
