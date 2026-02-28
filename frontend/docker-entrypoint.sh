#!/bin/sh
set -e

export API_URL="${API_URL:-http://docfabric-server:8000}"

envsubst '${API_URL}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf
