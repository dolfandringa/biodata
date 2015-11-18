import datetime
from biodata.model import datasets
import wtforms
from sqlalchemy import types as sa_types
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import RelationshipProperty, ColumnProperty
from collections import OrderedDict
import decimal

def get_object(datasetname,classname):
    """
    Maps a strings for datasetname and classname to the correct
    SQLAlchemy object for that dataset and class
    """
    ds = dict([(cls.__name__.split('.')[-1],cls) for cls in datasets])
    dataset = ds[datasetname]
    classes = dict([(obj.__name__.lower(),obj) for obj in dataset.tables])
    cls = classes[classname]
    return cls

def json_desired():
    """
    Checks http_accept header of the request.
    Returns true if the best match is application/json.
    Returns false otherwise.
    """
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']

def validator(message,func):
    """
    Wrapper around the our validator functions to work with wtforms. 
    It should get a message string which for validation failure and a 
    function which returns a bool to check valid input.
    """
    def wrapper(form,field):
        validates = func(field.data)
        if not validates and field.data is not None:
            raise wtforms.ValidationError(message)
    return wrapper

__type_map = {
    sa_types.Integer: {'widget':wtforms.IntegerField},
    sa_types.Numeric: {'widget':wtforms.DecimalField},
    sa_types.Unicode: {'widget':wtforms.StringField},
    sa_types.String: {'widget':wtforms.StringField},
    sa_types.UnicodeText: {'widget':wtforms.TextAreaField},
    sa_types.Date: {
        'widget':wtforms.DateField,
        'kwargs':{'description':" format: YYYY-MM-DD",
                  'format': '%Y-%m-%d'}},
    sa_types.Time: {
        'widget':wtforms.DateTimeField,
        'kwargs':{'description':" format: HH:MM",
                  'format': '%H:%M'}},
}

def map_column_type(c):
    """
    Maps an SQLAlchemy column type to a wtform field including validators.
    Returns a dictionary with widget being the wtform field
    label being the label for the field and args and kwargs being the
    additional arguments for the field.
    """
    field =  __type_map.get(c.type.__class__)
    args=field.get('args',[])
    
    if not c.nullable:
        args.append(wtforms.validators.InputRequired())
    kwargs=field.get('kwargs',{})
    return {'widget':field['widget'],'label':c.name,'args':args,'kwargs':kwargs}


def get_data_attributes(obj):
    """
    Get all the data attributes (table columns/relationships, etc)
    for an SQLALchemy object.
    """
    for prop in dir(obj):
        attr = getattr(obj,prop)
        if not hasattr(attr,'property'):
            continue
        if hasattr(obj,'formfields') and prop in obj.formfields.keys() and obj.formfields[prop].get('skip',False)==True:
            #This property should be skipped for the interface
            continue
        yield attr

def get_colnames(cls):
    """
    Retrieves all the field names for an sqlalchemy class, including
    relation attributes.
    """
    columns = [c.name for c in get_simple_columns(cls)]
    rel_columns = [c.key for c in get_relation_attributes(cls)]
    rel_multi_columns = [c.key for c in get_multi_relation_attributes(cls)]
    return columns+rel_columns+rel_multi_columns

def get_values(inst):
    """
    Retrieves all the values for an SQLAlchemy instance (table row).
    It converts list values (like one-to-many relation attributes) 
    into a comma separated string of string representations of the list items.
    """
    values = []
    for c in get_colnames(inst.__class__):
        v=getattr(inst,c)
        if isinstance(v,list):
            v=",".join([v2 and str(v2) or None for v2 in v])
        else:
            v=v and wtforms.utils.intget(v) or (v and str(v) or None)
        values.append((c,v))
    values.append(('id',inst.id))
    return OrderedDict(values)


def get_simple_columns(obj):
    """
    Retrieves the 'normal' fields for an SQLAlchemy object. This excludes
    any fields defined through relationship attributes.
    """
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
    """
    Gets all one-to-many relationship attributes for an SQLAlchemy object.
    """
    for attr in get_data_attributes(obj):
        if isinstance(attr.property,RelationshipProperty):
            if attr.property.uselist == True:
                #skip the property if it is on the Many side of One-to-Many
                #or Many-to-Many relationships
                continue
            yield attr

def get_multi_relation_attributes(obj):
    """
    Gets all many-to-many relationship attributes for an SQLAlchemy object.
    """
    for attr in get_data_attributes(obj):
        prop=attr.property
        if isinstance(prop,RelationshipProperty) and prop.backref!=None:
            target = prop.mapper.entity
            target_prop = getattr(target,prop.backref).property
            if prop.uselist == True and target_prop.uselist == True:
                #this is a Many-to-Many relationship
                yield attr

def get_primary_keys(obj):
    """
    Gets all primary keys for an SQLAlchemy object.
    """
    return [c.name for c in inspect(obj).primary_key]

def get_fields(obj,orm):
    """
    Gets wtform fields for all attributes of an SQLAlchemy object.
    It maps SQLAlchemy attributes to wtform fields, taking relationship 
    attributes (one-to-many and many-to-many) into account.
    """
    fields = OrderedDict()
    for attr in get_relation_attributes(obj):
        #turn foreign keys into dropdowns with the id as value 
        #and the column "name" as description
        target = attr.property.mapper.entity
        values = orm.query(target).all()
        fname = getattr(target,'pretty_name',attr.key)
        fields[fname]={ 
            'widget':wtforms.SelectField,
            'label':fname,
            'kwargs':{
                'choises':[[(v.id, str(v)) for v in values]],
                'description':
                    "<a class='addlink' href='%s/new'>Add %s</a>"%(fname,fname),
                'data-values_url':'%s/'%fname}}
    for attr in get_multi_relation_attributes(obj):
        #turn foreign keys for many-to-many relations into dropdowns with the id as value 
        #and the column "name" as description
        #the dropdown should allow multiple values
        target = attr.property.mapper.entity
        values = orm.query(target).all()
        fname = getattr(target,'pretty_name',target.__name__)
        fields[fname]={ 
            'widget':wtforms.SelectMultipleField,
            'label':attr.key,
            'kwargs':{
                'choices':[[(v.id, str(v)) for v in values]],
                'description':
                    "<a class='addlink' href='%s/new'>Add %s</a>"%(fname,fname),
                'data-values_url':'%s/'%fname}}
    for c in get_simple_columns(obj):
        #map the form widgets by the SQLAlchemy column type
        fields[c.name]=map_column_type(c)

    if hasattr(obj,'formfields'):
        #adjust the widgets by the arguments defined in the model
        for k,v in obj.formfields.items():
            field = fields.get(k,{})
            if v.get('skip',False) == True:
                continue
            args = v.get('args',field.get('args',[]))
            kwargs = field.get('kwargs',{})
            kwargs.update(v.get('kwargs',{}))
            widget = v.get('widget',field.get('widget'))
            fields[k] = {'label':k,'widget':widget,'args':args,'kwargs':kwargs}

    for k,v in fields.items():
        #instantiate the widgets
        print ("k: %s v:%s"%(k,v))
        fields[k]=v['widget'](v['label'],*v['args'],**v['kwargs'])
    fields.values()[0].attrs['autoFocus']=True

    return fields