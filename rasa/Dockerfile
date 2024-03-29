# builder stage
FROM python:3.8-bullseye AS builder

# install packages.
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
            --extra-index-url https://download.pytorch.org/whl/cpu \
            rasa[jieba,transformers]==3.6.9 \
            torch==2.0.1+cpu \
            ckip-transformers \
            line-bot-sdk \
        ;

# release stage
FROM python:3.8-slim-bullseye AS release

# python venv
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# replace initial project
COPY ./build/initial_project_zh /app

# set HOME
ENV HOME=/app
WORKDIR /app

# create volumes
VOLUME ["/tmp", "/app", "/data"]

# change shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# the entry point
EXPOSE 5005
ENTRYPOINT ["rasa"]
CMD ["run", "--enable-api", "--cors=\"*\""]
