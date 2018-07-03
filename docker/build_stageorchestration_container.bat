SET PATH_BUILD=..
docker build -t superlimitbreak/stageorchestration_base:latest --file .\stageOrchestration.base.dockerfile .
docker build -t superlimitbreak/stageorchestration:latest --file .\stageOrchestration.production.dockerfile %PATH_BUILD%

REM docker push superlimitbreak/stageorchestration:latest
