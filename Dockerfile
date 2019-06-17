FROM python:alpine as base

# https://blog.sneawo.com/blog/2017/09/07/how-to-install-pillow-psycopg-pylibmc-packages-in-pythonalpine-image/
RUN apk add --no-cache jpeg-dev zlib-dev
COPY requirements.pip requirements.pip
RUN apk add --no-cache \
        --virtual .build-deps build-base linux-headers git &&\
    pip3 install --no-cache-dir -r requirements.pip &&\
    apk del .build-deps

WORKDIR /stageOrchestration
ENTRYPOINT ["python3", "server.py"]
CMD [ "--config", "config.docker.yaml" ]

COPY ./ ./

FROM base as test
RUN pytest --doctest-modules

FROM base
#--config config.development.yaml --subscriptionserver_host display_trigger_server

# docker run --rm -it -p 23487:23487 superlimitbreak/stageorchestration --config config.production.yaml

# TODO: production - copy stageOrchestration code into container
