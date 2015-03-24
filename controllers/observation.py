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
    ORM_CLS = rvc_species.Observation

app = web.application(urls, locals())
