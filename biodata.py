import os
import sys
curdir = os.path.abspath(os.path.dirname(__file__))
os.chdir(curdir)
sys.path.append(curdir)

import web
from controllers import sample
from controllers.dynamic_controller import getApplication
from sqlalchemy.orm import scoped_session, sessionmaker
import model
import sys
import logging as log

web.config.debug = False

log.basicConfig(stream=sys.stdout,level=log.DEBUG,format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

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
        return render.new()

class index:
    def GET(self):
        datasets = [d.__name__.split('.')[-1] for d in model.datasets]
        return render.index(datasets)

urls = [
    "/", index
]

for dataset in [d.__name__.split('.')[-1] for d in model.datasets]:
    ds_urls = ["/new",new]
    for obj in getattr(model,dataset).tables:
        application = getApplication(obj)
        name = obj.__name__.lower()
        ds_urls += ["/%s"%name,application]
    ds_app = web.application(tuple(ds_urls), locals(), autoreload=False)
    print("adding application for dataset %s with urls %s"%(dataset,ds_urls))
    urls.append("/%s"%dataset)
    urls.append(ds_app)

app = web.application(tuple(urls), globals(),autoreload=False)
print(app.mapping)
app.add_processor(load_sqla)

if __name__ == "__main__":
    app.run()
else:
    application = app.wsgifunc()
