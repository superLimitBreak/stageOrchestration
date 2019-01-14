FROM python:3

RUN pip3 install --upgrade pip setuptools virtualenv

COPY requirements.pip requirements.pip
RUN pip3 install -r requirements.pip

WORKDIR /stageOrchestration
ENTRYPOINT ["python3", "server.py"]
CMD [ "--config", "config.docker.yaml" ]

COPY ./ ./


#--config config.development.yaml --displaytrigger_host display_trigger_server

# docker run --rm -it -p 23487:23487 superlimitbreak/stageorchestration --config config.production.yaml

# TODO: production - copy stageOrchestration code into container
