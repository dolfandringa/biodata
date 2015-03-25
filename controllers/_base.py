from web import form
import web
from util import get_fields, get_relation_attributes, get_simple_columns,get_values
#import pdb

render = web.template.render('templates/')


class BaseShowController:

    def GET(self,id):
        print('id: %s'%id)
        cls=self.__class__.ORM_CLS
        inst=web.ctx.orm.query(cls).get(id)
        print inst
        if inst==None:
            raise web.InternalError("Error 500: %s with id %s not found"%(cls.__name__,id))
        fields=get_values(inst)
        print(fields)
        return render.show(cls.__name__,id,fields)

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
        source={}
        for k,v in web.input().items():
            #convert integers to int values
            v=form.utils.intget(v) or v
            source[k]=v
        defaults.update(source)
        f.fill(source=defaults)
        return f

    def store_values(self,obj,orm):
        f = self.get_form(obj,orm)
        source=dict([(k,form.utils.intget(v) or v) for k,v in web.input().items()])
        if not f.validates(source=source):
            #Validation failed. Back to the form with the error message
            ID = self.__class__.ID
            TITLE = self.__class__.TITLE
            return render.form(f,ID,TITLE,web.url())
        else:
            #The form validated. Store the values in the db
            inst = obj()
            for col in get_simple_columns(obj):
                #set the simple column values
                setattr(inst,col.name,f[col.name].value or None)
            for attr in get_relation_attributes(obj):
                #get the relation attributes and set them.
                target = attr.property.mapper.entity #target class
                pkey = f[attr.key].value #primary key value from the form
                val = orm.query(target).get(pkey) #get target instance from pkey
                setattr(inst,attr.key,val)
            orm.add(inst)
            orm.commit()
            #handle the resulting redirection.
            if 'HTTP_X_REQUESTED_WITH' in web.ctx.environ.keys():
                #we're dealing with an ajax request
                if f['redirect'].value == 'form':
                    #back to the form with the same values.
                    f.fill(source=dict([(k.name,k.value) for k in f.inputs if isinstance(k,form.Dropdown)]))
                    return render.form(f,self.__class__.ID,self.__class__.TITLE, web.url())
                else:
                    #show the added item
                    return web.seeother('/%s'%inst.id)
            elif f['redirect'].value == 'form':
                #redirect to the form again, empty values in the form first
                f.fill(source=dict([(k.name,None) for k in f.inputs]))
                return render.form(f,self.__class__.ID,self.__class__.TITLE, web.url())
            else:
                #redirect to the list page
                return web.seeother('/')
