FROM nginx:1.25-alpine

RUN apk add --no-cache openssl \
    && rm -f /etc/nginx/conf.d/default.conf

ARG NGINX_CONFIG=nginx.staging.conf
COPY proxy_params.conf /etc/nginx/proxy_params.conf
COPY ${NGINX_CONFIG} /etc/nginx/nginx.conf
COPY docker-entrypoint.sh /docker-entrypoint.d/40-tamor-init.sh
RUN chmod +x /docker-entrypoint.d/40-tamor-init.sh
