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
    ORM_CLS = rvc_species.Species

app = web.application(urls, locals())
