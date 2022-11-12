FROM node:16-bullseye AS builder
COPY ./app /app
WORKDIR /app
RUN set -eux; \
        npm install; \
        npm run build;

FROM nginx:latest AS release
RUN mkdir /app
COPY --from=builder /app/dist /app
COPY ./templates /etc/nginx/templates
ENV NGINX_PORT=80 \
    RASA_API_PROTOCOL=http \
    RASA_API_HOST=rasa \
    RASA_API_PORT=5005 \
    ASAR_API_PROTOCOL=http \
    ASAR_API_HOST=api \
    ASAR_API_PORT=5500


