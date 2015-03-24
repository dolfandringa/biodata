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
        samples = web.ctx.orm.query(rvc_species.Sample).all()
        return render.sample_list(samples)

class new(BaseController):
    ID = "sample"
    TITLE = "New Sample"
    ORM_CLS = rvc_species.Sample

app = web.application(urls, locals())
