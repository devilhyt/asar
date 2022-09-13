FROM mcr.microsoft.com/vscode/devcontainers/python:3.10

COPY ./app/requirements.txt .
RUN set -eux; \
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

WORKDIR /app

ENTRYPOINT [ "gunicorn" ]
CMD ["-h"]