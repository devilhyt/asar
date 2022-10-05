FROM rasa:base

RUN rm -rf /opt/venv/lib/python3.8/site-packages/rasa/cli/initial_project

COPY ./build/initial_project_zh /opt/venv/lib/python3.8/site-packages/rasa/cli/initial_project

RUN set -eux; \
        pip install -U --no-cache-dir \
            ckip-transformers \
        ;