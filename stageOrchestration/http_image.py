import os
from itertools import chain

import falcon

from calaldees.files.exts import file_ext
from calaldees.string_tools import random_string

from stageOrchestration.sequence_manager import SequenceManager

import logging
log = logging.getLogger(__name__)


class HTTPImageRenderMixin():
    SUPPORTED_IMAGE_FORMATS = {'png', 'jpeg', 'jp2', 'tiff', 'bmp', 'webp'}  # 'avif',

    def __init__(self, options):
        self.sequence_manager = SequenceManager(**options)
        self.options = options
        self.instance_id = random_string() if options.get('postmortem') else ''

    def get_etag(self, sequence_name):
        # Hash fallback - should not be used as lights and media have differing hashs
        return self.sequence_manager.get_rendered_hash(sequence_name)

    def on_get(self, request, response, sequence_name=None):
        # Args
        sequence_name, file_extension = file_ext(sequence_name)
        kwargs = {
            k: v
            for k, v in {
                **self.DEFAULT_kwargs,
                **self.options,
                **request.params,
            }.items()
            if k in self.DEFAULT_kwargs.keys()
        }
        if file_extension:
            kwargs['image_format'] = file_extension
        kwargs['sequence_name'] = sequence_name

        # Exists
        if not self.sequence_manager.exists(kwargs['sequence_name']):
            response.media = {'error': 'file not found'}
            response.status = falcon.HTTP_400
            return

        # ETag
        content_etag = '|'.join(chain(
            (
                self.instance_id,
                (
                    # TODO: this dosnt look right? cachebust will always trump sequence hash?
                    request.params.get('cachebust')
                    or
                    self.get_etag(kwargs['sequence_name'])
                ),
            ),
            map(str, kwargs.values()),
        ))
        if content_etag in (request.if_none_match or ''):
            response.status = falcon.HTTP_304
            return
        response.etag = content_etag

        # Render
        try:
            response.body = self.render(**kwargs)
        except Exception as ex:
            log.exception(ex)
            response.media = {'error': 'unable to render image', 'reason': f'{type(ex)} {str(ex)}', 'kwargs': kwargs}
            response.status = falcon.HTTP_500
            return

        # MIME Type
        if kwargs['image_format'] not in self.SUPPORTED_IMAGE_FORMATS:
            response.status = falcon.HTTP_400
            response.media = {'error': f'invalid image format. Supported formats are {self.SUPPORTED_IMAGE_FORMATS}'}
            return
        response.content_type = f"image/{kwargs['image_format']}"

        response.status = falcon.HTTP_200
