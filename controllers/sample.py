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

    def GET(self):
        f = self.get_form(rvc_species.Sample,web.ctx.orm)
        return render.form(f,new.ID,new.TITLE)

    def POST(self):
        return self.store_values(rvc_species.Sample,web.ctx.orm)

app = web.application(urls, locals())
