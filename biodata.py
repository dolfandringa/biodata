import web
#from controllers import site, sample, observation, species, observer
from controllers.dynamic_controller import getApplication
from sqlalchemy.orm import scoped_session, sessionmaker
import model
import sys
import logging
import pdb

web.config.debug = False

logging.basicConfig(stream=sys.stdout,level=logging.DEBUG,format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

def load_sqla(handler):
    web.ctx.orm = scoped_session(sessionmaker(bind=model.engine))
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

render = web.template.render('templates/')

class new:
    def GET(self):
        pdb.set_trace()
        dataset = web.input().dataset
        dataset = getattr(model,dataset)
        for obj in dataset.tables:
            application = getApplication(obj)
            name=obj.__name__.lower()
            print('adding mapping for %s to %s'%(name,application))
            app.add_mapping(name,application)
        return render.new()

class index:
    def GET(self):
        datasets = [d.__name__.split('.')[-1] for d in model.datasets]
        return render.index(datasets)

urls = (
    "/", index,
    "/new", new,
#    "/site", site.app,
#    "/sample", sample.app,
#    "/observation", observation.app,
#    "/observer", observer.app,
#    "/species", species.app
)
app = web.application(urls, globals())
app.add_processor(load_sqla)

if __name__ == "__main__":
    app.run()
