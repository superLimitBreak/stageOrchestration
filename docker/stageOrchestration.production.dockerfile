FROM superlimitbreak/stageorchestration_base:latest

COPY \
    ambilightEncoder.py \
    renderSequencePng.py \
    server.py \
./

COPY \
    stageOrchestration \
stageOrchestration/

COPY \
    data \
data/

COPY \
    config.production.yaml \
    config.development.yaml \
./

CMD [ "--config", "config.production.yaml" ]