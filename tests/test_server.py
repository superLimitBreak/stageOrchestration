import pytest


@pytest.fixture
def server(mocker):
    MockSequenceManager = mocker.patch('stageOrchestration.server.SequenceManager')
    from stageOrchestration.server import StageOrchestrationServer
    server = StageOrchestrationServer()
    return server


def test_network_event():
    pass


def test_scan_update_event():
    #mocker.patch('stageOrchestration.events.model.triggerline.TriggerLine')
    #from stageOrchestration.events.model.triggerline import TriggerLine
    #tt = TriggerLine()
    #assert False
    pass


def test_frame_event(server):
    server.frame_event(0)
