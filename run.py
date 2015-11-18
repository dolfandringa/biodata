from biodata import app, db, init_db
from controller import basebp

init_db()
app.register_blueprint(basebp)

if __name__=='__main__':
    app.run()