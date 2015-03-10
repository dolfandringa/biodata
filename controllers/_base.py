from web import form
import web
from util import get_fields, get_relation_attributes, get_simple_columns

render = web.template.render('templates/')

class BaseController:

    def get_form(self,obj,orm):
        return form.Form(*get_fields(obj,orm))()

    def store_values(self,obj,orm):
        f = self.get_form(obj,orm)
        if not f.validates():
            print('not validated')
            return render.form(f)
        else:
            print('we validated')
            inst = obj()
            for col in get_simple_columns(obj):
                setattr(inst,col.name,f[col.name].value or None)
            for attr in get_relation_attributes(obj):
                target = attr.property.mapper.entity
                print('target: %s, type: %s'%(target,type(target)))
                pkey = f[attr.key].value
                print("attribute: %s, id: %s"%(attr.key,pkey))
                val = orm.query(target).get(pkey)
                print('value: %s'%val)
                setattr(inst,attr.key,val)
            orm.add(inst)
            return web.seeother('/')
