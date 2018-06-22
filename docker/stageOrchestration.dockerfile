FROM python:3
RUN pip3 install --upgrade pip setuptools virtualenv
COPY stageOrchestration.pip requirements.pip
RUN pip3 install -r requirements.pip

WORKDIR /stageOrchestration
ENTRYPOINT ["python3", "server.py"]
#--config config.development.yaml --displaytrigger_host display_trigger_server

# TODO: production - copy stageOrchestration code into container
