
import os
import yaml

from os.path import join


def get_config(path=None):
    path = path or join(os.environ['HOME'], '.rdf_demo_rc')
    return tuple(yaml.safe_load_all(open(path)))[0]
