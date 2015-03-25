import web
from web import form
from model import *
from _base import BaseController, BaseShowController
from util import get_values, get_colnames

urls = (
    "/", "list",
    "/new", "new",
    "/(.+)", "show"
)

render = web.template.render('templates/')


class list:
    def GET(self):
        sampleid = web.input(sampleid=None).sampleid
        if sampleid != None:
            observations = web.ctx.orm.query(rvc_species.Observation).filter_by(sample_id=sampleid).all()
        else:
            observations = web.ctx.orm.query(rvc_species.Observation).all()
        return render.observation_list([get_values(o) for o in observations],get_colnames(rvc_species.Observation))


class show(BaseShowController):
    ORM_CLS=rvc_species.Observation


class new(BaseController):
    ID = 'observation'
    TITLE = 'New Observation'
    ORM_CLS = rvc_species.Observation

app = web.application(urls, locals())
