FROM python:3.10-bullseye AS builder

COPY ./app/requirements.txt .
RUN set -eux; \
        python -m venv /opt/venv; \
        . /opt/venv/bin/activate; \
        pip install -U --no-cache-dir \
            pip \
        ; \
        pip install -U --no-cache-dir \
            setuptools \
            wheel \
        ; \
        pip install -U --no-cache-dir \
            -r requirements.txt \
        ;

FROM python:3.10-slim-bullseye AS release

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./app /app

RUN mkdir -p /actions /data
VOLUME ["/actions", "/data"]

ENV RASA_API_PROTOCOL=http \
    RASA_API_HOST=rasa \
    RASA_API_PORT=5005 \
    ASAR_API_PROTOCOL=http \
    ASAR_API_HOST=api \
    ASAR_API_PORT=5500 \
    RASA_ACTIONS_ROOT=/actions

WORKDIR /app
ENTRYPOINT [ "gunicorn" ]
CMD ["--bind=0.0.0.0:5500", "--worker-class=gthread", "--workers=1", "--threads=4", "asar_api:create_app()" ]