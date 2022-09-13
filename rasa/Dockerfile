FROM rasa:base

RUN rm -rf /opt/venv/lib/python3.8/site-packages/rasa/cli/initial_project
COPY ./build/initial_project /opt/venv/lib/python3.8/site-packages/rasa/cli/initial_project