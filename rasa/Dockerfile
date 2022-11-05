# builder stage
FROM python:3.8-bullseye AS builder

# install packages.
COPY ./build/package /build/package
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
            numpy==1.19.5 \
        ; \
        pip install -U --no-cache-dir \
            -f /build/package/wheels \
            -f https://tf.kmtea.eu/whl/stable.html \
            rasa[jieba,transformers]==3.2.8 \
            tokenizers==0.10.2 \
        ; \
        pip install -U --no-cache-dir \
            numpy \
            ckip-transformers \
        ;

# release stage
FROM python:3.8-bullseye AS release

# python venv
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# replace initial project
RUN rm -rf /opt/venv/lib/python3.8/site-packages/rasa/cli/initial_project
COPY ./build/initial_project_zh /opt/venv/lib/python3.8/site-packages/rasa/cli/initial_project
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
CMD ["run", "--enable-api"]
