import pytest

from stageOrchestration.server import StageOrchestrationServer


def test_network_event__load_sequence(mocker):
    MockSequenceManager = mocker.patch('stageOrchestration.server.SequenceManager')()
    MockFrameReader = mocker.patch('stageOrchestration.server.FrameReader')
    server = StageOrchestrationServer()

    event = {'func': 'lights.load_sequence', 'sequence_module_name': 'test'}
    server.network_event(event)

    MockSequenceManager.exists.assert_called_with('test')
    MockSequenceManager.get_rendered_hash.assert_called_with('test')
    MockSequenceManager.get_meta.assert_called_with('test')
    MockSequenceManager.get_rendered_filename.assert_called_with('test')
    MockSequenceManager.get_triggerline.assert_called_with('test')


def test_scan_update_event(mocker):
    MockSequenceManager = mocker.patch('stageOrchestration.server.SequenceManager')
    MockSubscriptionClient = mocker.patch('stageOrchestration.server.StageOrchestrationServer.NullSubscriptionClient')()
    server = StageOrchestrationServer()

    server.scan_update_event(())

    MockSubscriptionClient.send_message.assert_called_with({
        'deviceid': 'light_visulisation',
        'func': 'scan_update_event',
        'sequence_files': (),
        'sequence_module_name': '',
        'module_hash': '',
    })


def test_frame_event(mocker):
    MockSequenceManager = mocker.patch('stageOrchestration.server.SequenceManager')
    MockSubscriptionClient = mocker.patch('stageOrchestration.server.StageOrchestrationServer.NullSubscriptionClient')()
    server = StageOrchestrationServer()

    server.frame_event(0)

    MockSubscriptionClient.send_message.called
