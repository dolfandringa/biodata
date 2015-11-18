from biodata import app, db, init_db
from controller import basebp
from flask import g

init_db()
app.register_blueprint(basebp)

@app.before_request
def load_db():
    g.db = g.get('db', db )

if __name__=='__main__':
    app.run()