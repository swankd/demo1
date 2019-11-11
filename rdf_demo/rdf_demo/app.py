
from flask import Flask

from .config import get_config
from .graph import HDTGraph

config = get_config()
app = Flask('rdf_demo')
app.graph = HDTGraph(config['hdt_file_path'])

from . import views
