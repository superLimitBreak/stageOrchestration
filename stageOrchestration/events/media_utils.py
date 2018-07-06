import os.path

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata


def hachoir_metadata(filename):
    return extractMetadata(createParser(filename))


class MediaInfo():
    def __init__(self, path):
        self.path = path

    def metadata(self, filename):
        return hachoir_metadata(os.path.join(self.path, filename))
        # .get('duration')
