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
    ORM_CLS = rvc_species.Sample


class show(BaseShowController):
    ORM_CLS=rvc_species.Sample


class new(BaseController):
    ID = "sample"
    TITLE = "New Sample"
    ORM_CLS = rvc_species.Sample

app = web.application(urls, locals())
