import web
from web import form
from model import *
from _base import BaseController, BaseShowController, BaseListController
import pdb
from collections import OrderedDict
import json

urls = (
    "/", "list",
    "/new", "new",
    "/(.+)", "show"

)

render = web.template.render('templates/')



class list(BaseListController):
    ORM_CLS = rvc_species.Site


class show(BaseShowController):
    ORM_CLS=rvc_species.Site


class new(BaseController):
    ID = "site"
    TITLE = "New Site"
    ORM_CLS = rvc_species.Site

app = web.application(urls, locals())
