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
        species = web.ctx.orm.query(rvc_species.Species).all()
        return render.species_list(species)

class new(BaseController):
    ID = 'species'
    TITLE = 'New Species'
    def GET(self):
        f = self.get_form(rvc_species.Species,web.ctx.orm)
        return render.form(f,new.ID,new.TITLE)

    def POST(self):
        return self.store_values(rvc_species.Species,web.ctx.orm)

app = web.application(urls, locals())
