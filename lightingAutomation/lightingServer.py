import logging
log = logging.getLogger(__name__)


def serve(**kwargs):
    log.info('Serve {}'.format(kwargs))
