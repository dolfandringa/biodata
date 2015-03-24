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
        sites = web.ctx.orm.query(rvc_species.Site).all()
        return render.sites_list(sites)

class new(BaseController):
    ID = "site"
    TITLE = "New Site"
    ORM_CLS = rvc_species.Site

app = web.application(urls, locals())
