from web import form
import web
from util import get_fields, get_relation_attributes, get_simple_columns

render = web.template.render('templates/')

class BaseController:

    def GET(self):
        f = self.get_form(self.__class__.ORM_CLS,web.ctx.orm)
        return render.form(f, self.__class__.ID, self.__class__.TITLE, web.url())

    def POST(self):
        return self.store_values(self.__class__.ORM_CLS,web.ctx.orm)

    def get_form(self,obj,orm):
        fields=get_fields(obj,orm).values()
        redirf=form.Hidden(name='redirect',value='list')
        fields.append(redirf)
        f = form.Form(*fields)()
        defaults=dict([(i.name,i.value) for i in f.inputs])
        source=web.input()
        defaults.update(source)
        f.fill(source=defaults)
        return f

    def store_values(self,obj,orm):
        f = self.get_form(obj,orm)
        if not f.validates():
            print('not validated')
            ID = self.__class__.ID
            TITLE = self.__class__.TITLE
            return render.form(f,ID,TITLE,web.url())
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
            if f['redirect'].value == 'form':
                #redirect to the form again, empty values the form first
                f.fill(source=dict([(k.name,None) for k in f.inputs]))
                return render.form(f,self.__class__.ID,self.__class__.TITLE, web.url())
            else:
                return web.seeother('/')
