import web
from web import form
from model import *
from util import get_fields, map_column_type

urls = (
    "/", "list",
    "/new", "new"
)

render = web.template.render('templates/')



class list:
    def GET(self):
        samples = web.ctx.orm.query(rvc_species.Sample).all()
        return render.sample_list(samples)

class new:

    def GET(self):
        sample_form = form.Form(*get_fields(rvc_species.Sample,web.ctx))
        f = sample_form()
        return render.form(f)

    def POST(self):
        sample_form = form.Form(*get_fields(rvc_species.Sample,web.ctx))
        f = sample_form()
        if not f.validates():
            return render.form(f)
        else:
            sample = rvc_species.Sample()
            sample.date = f['date'].value
            sample.time = f['time'].value
            site = web.ctx.orm.query(rvc_species.Site).filter_by(id=f['site'].value).one()
            sample.site = site
            web.ctx.orm.add(sample)
            return web.seeother('/')

app = web.application(urls, locals())
