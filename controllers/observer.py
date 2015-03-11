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

    def GET(self):
        f = self.get_form(rvc_species.Observer,web.ctx.orm)
        return render.form(f)

    def POST(self):
        res = self.store_values(rvc_species.Observer,web.ctx.orm)
        return res

app = web.application(urls, locals())
