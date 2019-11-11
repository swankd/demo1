
from flask import Flask

from bdb_tool import BdbRDFGraph
from .config import get_config

config = get_config()
app = Flask('rdf_demo')
app.graph = BdbRDFGraph(config['db_dir'])

from . import views
