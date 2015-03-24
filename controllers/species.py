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
        species = web.ctx.orm.query(rvc_species.Species).all()
        return render.species_list(species)


class show(BaseShowController):
    ORM_CLS=rvc_species.Species


class new(BaseController):
    ID = 'species'
    TITLE = 'New Species'
    ORM_CLS = rvc_species.Species

app = web.application(urls, locals())
