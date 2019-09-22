
from .app import app
from .db import DB

db = DB()


@app.route('/')
def root():
    return '<br>\n'.join([f'{db.nnouns} nouns',
                          f'{db.nverbs} verbs',
                          f'{db.nedges} edges'])
