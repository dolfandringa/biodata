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
        observations = web.ctx.orm.query(rvc_species.Observation).all()
        return render.observation_list(observations)

class new(BaseController):
    ID = 'observation'
    TITLE = 'New Observation'
    def GET(self):
        f = self.get_form(rvc_species.Observation,web.ctx.orm)
        return render.form(f,new.ID,new.TITLE)

    def POST(self):
        return self.store_values(rvc_species.Observation,web.ctx.orm)

app = web.application(urls, locals())
