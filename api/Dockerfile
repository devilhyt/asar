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

# start a new build stage
FROM python:3.10-bullseye

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir -p /data

WORKDIR /app

ENTRYPOINT [ "gunicorn" ]
CMD ["-h"]