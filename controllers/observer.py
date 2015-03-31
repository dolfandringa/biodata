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
    ORM_CLS = rvc_species.Observer
    TEMPLATE = render.observer_list


class show(BaseShowController):
    ORM_CLS=rvc_species.Observer


class new(BaseController):
    ID = "observer"
    TITLE = "New Observer"
    ORM_CLS = rvc_species.Observer

app = web.application(urls, locals())
