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
        sites = web.ctx.orm.query(rvc_species.Site).all()
        return render.sites_list(sites)

class new:

    def GET(self):
        site_form = form.Form(*get_fields(rvc_species.Site,web.ctx))
        f = site_form()
        return render.form(f)

    def POST(self):
        site_form = form.Form(*get_fields(rvc_species.Site,web.ctx))
        f = site_form()
        if not f.validates():
            return render.form(f)
        else:
            site = rvc_species.Site()
            site.name = f['name'].value
            site.barangay = f['barangay'].value
            site.municipality = f['municipality'].value
            site.lat = f['lat'].value
            site.lon = f['lon'].value
            web.ctx.orm.add(site)
            return web.seeother('/')

app = web.application(urls, locals())
