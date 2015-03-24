import web
from web import form
from model import *
from _base import BaseController

urls = (
    "/", "list",
    "/new", "new"
)

render = web.template.render('templates/')



class list:
    def GET(self):
        observers = web.ctx.orm.query(rvc_species.Observer).all()
        return render.observer_list(observers)

class new(BaseController):
    ID = "observer"
    TITLE = "New Observer"
    ORM_CLS = rvc_species.Observer

app = web.application(urls, locals())
