import web
import datetime
from web import form
from sqlalchemy import types as sa_types
from sqlalchemy.orm.properties import RelationshipProperty, ColumnProperty
from collections import OrderedDict

def is_int_date(v):
    print('checking date value %s'%v)
    try:
        datetime.datetime.strptime(v,'%Y-%m-%d')
        return True
    except ValueError:
        return False


__type_map = {
    sa_types.Integer: {
        'widget':form.Textbox,
        'args':[
            form.Validator(
                'Please enter a whole number (no decimals)',
                lambda v: form.utils.getint(v,None) != None
            )
        ]
    },
    sa_types.Unicode: {'widget':form.Textbox},
    sa_types.String: {'widget':form.Textbox},
    sa_types.UnicodeText: {'widget':form.Textarea},
    sa_types.Date: {
        'widget':form.Textbox,
        'kwargs':{'post':" format: YYYY-MM-DD"},
        'args':[form.Validator(
            'Not a valid date format.',
            is_int_date)]},
    sa_types.Time: {'widget':form.Textbox}
}

def map_column_type(c):
    field =  __type_map.get(c.type.__class__)
    args=field.get('args',[])
    if not c.nullable:
        args.append(form.notnull)
    kwargs=field.get('kwargs',{})
    return field['widget'](c.name,*args,**kwargs)


def get_data_attributes(obj):
    for prop in dir(obj):
        attr = getattr(obj,prop)
        if not hasattr(attr,'property'):
            continue
        yield attr

def get_values(inst):
    columns = [c.name for c in get_simple_columns(inst.__class__)]
    rel_columns = [c.key for c in get_relation_attributes(inst.__class__)]
    return dict([(c,str(getattr(inst,c))) for c in columns+rel_columns])


def get_simple_columns(obj):
    fields = []
    for attr in get_data_attributes(obj):
        if isinstance(attr.property,ColumnProperty):
            #this is a normal column property
            #map the column to it's form equivalent
            for c in attr.property.columns:
                if len(c.foreign_keys)>0:
                    #skip foreign keys
                    continue
                if c.primary_key:
                    #skip the primary key
                    continue
                yield c

def get_relation_attributes(obj):
    for attr in get_data_attributes(obj):
        if isinstance(attr.property,RelationshipProperty):
            if attr.property.uselist == True:
                #skip the property if it is on the Many side of One-to-Many
                #or Many-to-Many relationships
                continue
            yield attr

def get_fields(obj,orm):
    fields = OrderedDict()
    for attr in get_relation_attributes(obj):
        #turn foreign keys into dropboxes with the id as value 
        #and the column "name" as description
        target = attr.property.mapper.entity
        values = orm.query(target).all()
        fname = attr.key
        fields[fname]=form.Dropdown(
                        fname,
                        [(v.id, str(v)) for v in values],
                        post="<a href='/%s/new'>Add %s</a>"%(fname,fname))
    for c in get_simple_columns(obj):
        fields[c.name]=map_column_type(c)

    if hasattr(obj,'formfields'):
        for k,v in obj.formfields.items():
            args=v.get('args',[])
            kwargs=v.get('kwargs',{})
            fields[k]=v['widget'](k,*args,**kwargs)
    return fields
