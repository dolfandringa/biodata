import web
import datetime
from web import form
from sqlalchemy import types as sa_types
from sqlalchemy.orm.properties import RelationshipProperty, ColumnProperty
from collections import OrderedDict


def parse_accept(header):
    """Parses Accept: header.
        >>> parse_accept("text/plain; q=0.5, text/html")
        [{'media_type': 'text/html'}, {'q': 0.5, 'media_type': 'text/plain'}]
    """
    result= []
    for media_range in header.split(','):
        parts = media_range.split(';')
        media_type = parts.pop(0).strip()
        d = {'media_type': media_type}
        for part in parts:
            try:
                k, v = part.split('=')
                d[k.strip()] = v.strip()
            except (IndexError, ValueError):
                pass

        try:
            if 'q' in d:
                d['q'] = float(d['q'])
        except ValueError:
            del d['q']

        result.append(d)
    result.sort(key=lambda m: m.get('q', 1.0), reverse=True)
    return result

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
                lambda v: form.utils.intget(v,None) != None
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
        if hasattr(obj,'formfields') and prop in obj.formfields.keys() and obj.formfields[prop].get('skip',False)==True:
            #This property should be skipped for the interface
            continue
        yield attr

def get_colnames(cls):
    columns = [c.name for c in get_simple_columns(cls)]
    rel_columns = [c.key for c in get_relation_attributes(cls)]
    rel_multi_columns = [c.key for c in get_multi_relation_attributes(cls)]
    return columns+rel_columns+rel_multi_columns

def get_values(inst):
    values = []
    for c in get_colnames(inst.__class__):
        v=getattr(inst,c)
        if isinstance(v,list):
            v=",".join([v2 and str(v2) or None for v2 in v])
        else:
            v=v and form.utils.intget(v) or (v and str(v) or None)
        values.append((c,v))
    values.append(('id',inst.id))
    return OrderedDict(values)


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

def get_multi_relation_attributes(obj):
    for attr in get_data_attributes(obj):
        prop=attr.property
        if isinstance(prop,RelationshipProperty) and prop.backref!=None:
            target = prop.mapper.entity
            target_prop = getattr(target,prop.backref).property
            if prop.uselist == True and target_prop.uselist == True:
                #this is a Many-to-Many relationship
                yield attr

def get_fields(obj,orm):
    fields = OrderedDict()
    for attr in get_relation_attributes(obj):
        #turn foreign keys into dropdowns with the id as value 
        #and the column "name" as description
        target = attr.property.mapper.entity
        values = orm.query(target).all()
        fname = getattr(target,'pretty_name',attr.key)
        fields[fname]=form.Dropdown(
                        fname,
                        [(v.id, str(v)) for v in values],
                        post="<a class='addlink' href='%s/new'>Add %s</a>"%(fname,fname),
                        **{'data-values_url':'%s/'%fname})
    for attr in get_multi_relation_attributes(obj):
        #turn foreign keys for many-to-many relations into dropdowns with the id as value 
        #and the column "name" as description
        #the dropdown should allow multiple values
        target = attr.property.mapper.entity
        values = orm.query(target).all()
        fname = getattr(target,'pretty_name',target.__name__)
        fields[fname]=form.Dropdown(
                        attr.key,
                        [(v.id, str(v)) for v in values],
                        post="<a class='addlink' href='%s/new'>Add %s</a>"%(fname,fname),
                        **{'multiple':True,'data-values_url':'%s/'%fname})
    for c in get_simple_columns(obj):
        fields[c.name]=map_column_type(c)

    if hasattr(obj,'formfields'):
        for k,v in obj.formfields.items():
            if v.get('skip',False) == True:
                continue
            args=v.get('args',[])
            kwargs=v.get('kwargs',{})
            fields[k]=v['widget'](k,*args,**kwargs)
    fields.values()[0].attrs['autoFocus']=True
    return fields
