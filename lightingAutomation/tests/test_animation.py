import pytest

from ..animation.timeline import Timeline


@pytest.fixture()
def timeline():
    return Timeline()


def test_timeline_creation(timeline):
    pass
