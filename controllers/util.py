import web
from web import form
from sqlalchemy import types as sa_types
from sqlalchemy.orm.properties import RelationshipProperty, ColumnProperty

__type_map = {
    sa_types.Integer: (form.Textbox,form.Validator(
                        'Please enter a whole number (no decimals)',
                        lambda v: form.utils.getint(v,None) != None)),
    sa_types.Unicode: (form.Textbox,),
    sa_types.String: (form.Textbox,),
    sa_types.Date: (form.Textbox,),
    sa_types.Time: (form.Textbox,)
}


def map_column_type(c):
   field =  __type_map.get(c.type.__class__)
   return field[0](c.name,*field[1:])

def get_fields(obj,ctx):
    fields = []
    for prop in dir(obj):
        attr = getattr(obj,prop)
        if not hasattr(attr,'property'):
            continue
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
                fields.append(map_column_type(c))
        if isinstance(attr.property,RelationshipProperty):
            #turn foreign keys into dropboxes with the id as value 
            #and the column "name" as description
            if attr.property.uselist == True:
                #skip the property if it is on the Many side of One-to-Many
                #or Many-to-Many relationships
                continue
            table = attr.property.target
            values = ctx.orm.query(table).all()
            fname = attr.key
            fields.append(form.Dropdown(
                            fname,
                            [(v.id, v.name) for v in values],
                            post="<a href='/%s/new'>Add %s</a>"%(fname,fname)))
    return fields
