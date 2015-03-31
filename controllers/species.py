import web
from web import form
from model import *
from _base import BaseController, BaseShowController, BaseListController

urls = (
    "/", "list",
    "/new", "new",
    "/(.+)", "show"

)

render = web.template.render('templates/')



class list(BaseListController):
    ORM_CLS = rvc_species.Species
    TEMPLATE = render.species_list


class show(BaseShowController):
    ORM_CLS=rvc_species.Species


class new(BaseController):
    ID = 'species'
    TITLE = 'New Species'
    ORM_CLS = rvc_species.Species

app = web.application(urls, locals())
