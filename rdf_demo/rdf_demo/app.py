
from flask import Flask

app = Flask('rdf_demo')

from . import views
