
from .config import get_config

from bdb_tool import BdbRDFGraph

_config = get_config()
graph = BdbRDFGraph(_config['db_dir'])
