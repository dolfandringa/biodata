import web
from web import form
from model import *
from _base import BaseController, BaseShowController

urls = (
    "/", "list",
    "/new", "new",
    "/(.+)", "show"

)

render = web.template.render('templates/')



class list:
    def GET(self):
        observers = web.ctx.orm.query(rvc_species.Observer).all()
        return render.observer_list(observers)


class show(BaseShowController):
    ORM_CLS=rvc_species.Observer


class new(BaseController):
    ID = "observer"
    TITLE = "New Observer"
    ORM_CLS = rvc_species.Observer

app = web.application(urls, locals())
