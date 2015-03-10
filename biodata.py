import web
from controllers import site, sample, observation
from sqlalchemy.orm import scoped_session, sessionmaker
from model import *

def load_sqla(handler):
    web.ctx.orm = scoped_session(sessionmaker(bind=engine))
    try:
        return handler()
    except web.HTTPError:
       web.ctx.orm.commit()
       raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()
        # If the above alone doesn't work, uncomment 
        # the following line:
        #web.ctx.orm.expunge_all()

class index:
    def GET(self):
        return 'Hello world!'

urls = (
    "", "index",
    "/site", site.app,
    "/sample", sample.app,
    "/observation", observation.app
)
app = web.application(urls, globals())
app.add_processor(load_sqla)

if __name__ == "__main__":
    app.run()
