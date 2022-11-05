FROM node:lts-bullseye AS builder
COPY ./app /app
WORKDIR /app
RUN set -eux; \
        npm install; \
        npm run build;

FROM nginx:latest
RUN mkdir /app
COPY --from=builder /app/dist /app
COPY ./templates /etc/nginx/templates
ENV NGINX_PORT=80 \
    ASAR_API_PROTOCOL=http \
    ASAR_API_HOST=api \
    ASAR_API_PORT=5500