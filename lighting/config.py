import os.path
import yaml

from libs.misc import file_scan


#@staticmethod
def open_yaml(path, target_class=None):
    with open(path, 'rb') as file_handle:
        obj_data = yaml.load(file_handle)
        return target_class(obj_data) if target_class else obj_data


#@staticmethod
def open_path(path, target_class=None):
    """
    Open all yamls in a path by constructing an object for each file based on the 'target' class
    """
    objs = {}
    for file_info in file_scan(path, r'.*\.yaml$'):
        objs[file_info.file_no_ext] = open_yaml(file_info.absolute, target_class)
    return objs


class LightingConfig(object):

    PATH_CONFIG_FILE = 'config.yaml'

    def __init__(self, yamlpath):
        self.config = open_yaml(os.path.join(yamlpath, self.PATH_CONFIG_FILE))
