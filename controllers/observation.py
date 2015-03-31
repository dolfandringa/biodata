import web
from web import form
from model import *
from _base import BaseController, BaseShowController, BaseListController
from util import get_values, get_colnames

urls = (
    "/", "list",
    "/new", "new",
    "/(.+)", "show"
)

render = web.template.render('templates/')


class list(BaseListController):
    ORM_CLS = rvc_species.Observation

class show(BaseShowController):
    ORM_CLS=rvc_species.Observation


class new(BaseController):
    ID = 'observation'
    TITLE = 'New Observation'
    ORM_CLS = rvc_species.Observation

app = web.application(urls, locals())
