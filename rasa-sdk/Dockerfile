FROM rasa-sdk:base

# Use subdirectory as working directory
WORKDIR /app

# Copy any additional custom requirements
COPY ./requirements.txt ./

# Change back to root user to install dependencies
USER root

# Install extra requirements for actions code
RUN set -eux; \
        apt-get update; \
        apt-get install -y --no-install-recommends \
            gcc-aarch64-linux-gnu \
        ; \
        rm -rf /var/lib/apt/lists/*;

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


# Copy actions folder to working directory
COPY ./app/actions /app/actions

CMD ["start", "--actions=actions", "--auto-reload"]