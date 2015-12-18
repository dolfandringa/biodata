from biodata.model import datasets
import wtforms
from sqlalchemy import types as sa_types
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import RelationshipProperty, ColumnProperty
from collections import OrderedDict
from flask import request, url_for


def store_values(obj, orm, valuedict):
    """
    Store values for an object.

    :param obj: The SQLAlchemy object for which the values need to be stored
    :param orm: The SQLAlchemy session in which to store the values
    :param valuedict: A dictionary like object containing the values to store.
    """
    f = valuedict  # just for simplicity sake. I don't want to search/replace f
    values = []
    pkeys = get_primary_keys(obj)
    for pkey in pkeys:
        values.append((pkey, f[pkey] or None))
    for col in get_simple_columns(obj):
        # set the simple column values
        values.append((col.name, f[col.name] or None))
    for attr in get_relation_attributes(obj):
        # get the relation attributes and set them.
        target = attr.property.mapper.entity  # target class
        pkey = f[attr.key]  # primary key value from the valuedict
        val = orm.query(target).get(pkey)  # get target instance from pkey
        values.append((attr.key, val))
    for attr in get_multi_relation_attributes(obj):
        target = attr.property.mapper.entity  # target class
        vals = []
        for v in f[attr.key]:
            val = orm.query(target).get(v)  # get target instance from pkey
            vals.append(val)
        values.append((attr.key, vals))
    values = OrderedDict(values)

    if all([pkey in values.keys() and values[pkey] is not None
            for pkey in pkeys]):
        # check if (all) primary keys have been defined,
        # if so, fetch the instance from the database.
        inst = orm.query(obj).get(tuple([values.get(pkey) for pkey in pkeys]))
    else:
        # if not, create a new instance
        inst = obj()
    for k, v in values.items():
        if isinstance(v, list):
            setattr(inst, k, [])  # empty the list first
            for val in v:
                getattr(inst, k).append(val)
        else:
            setattr(inst, k, v)
    orm.add(inst)
    orm.commit()
    return inst


def get_object(datasetname, classname):
    """
    Maps a strings for datasetname and classname to the correct
    SQLAlchemy object for that dataset and class
    """
    ds = dict([(cls.__name__.split('.')[-1], cls) for cls in datasets])
    dataset = ds[datasetname]
    classes = dict([(obj.__name__.lower(), obj) for obj in dataset.tables])
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


def validator(message, func):
    """
    Wrapper around the our validator functions to work with wtforms.
    It should get a message string which for validation failure and a
    function which returns a bool to check valid input.
    """
    def wrapper(form, field):
        validates = func(field.data)
        if not validates and field.data is not None:
            raise wtforms.ValidationError(message)
    return wrapper


__type_map = {
    sa_types.Integer: {'widget': wtforms.IntegerField},
    sa_types.Numeric: {'widget': wtforms.DecimalField},
    sa_types.Unicode: {'widget': wtforms.StringField},
    sa_types.String: {'widget': wtforms.StringField},
    sa_types.UnicodeText: {'widget': wtforms.TextAreaField},
    sa_types.Date: {
        'widget': wtforms.DateField,
        'kwargs': {'description': " format: YYYY-MM-DD",
                   'format': '%Y-%m-%d'}},
    sa_types.Time: {
        'widget': wtforms.DateTimeField,
        'kwargs': {'description': " format: HH:MM",
                   'format': '%H:%M'}},
}


def map_column_type(c):
    """
    Maps an SQLAlchemy column type to a wtform field including validators.
    Returns a dictionary with widget being the wtform field
    label being the label for the field and args and kwargs being the
    additional arguments for the field.
    """

    field = __type_map.get(c.type.__class__)
    args = field.get('args', [])

    if not c.nullable:
        args.append(wtforms.validators.InputRequired())
    else:
        args.append(wtforms.validators.Optional())
    kwargs = field.get('kwargs', {})
    html_attributes = field.get('html_attributes', {})
    return {'widget': field['widget'], 'label': c.name, 'args': args,
            'kwargs': kwargs, 'html_attributes': html_attributes}


def get_data_attributes(obj):
    """
    Get all the data attributes (table columns/relationships, etc)
    for an SQLALchemy object.
    """

    for prop in dir(obj):
        attr = getattr(obj, prop)
        if not hasattr(attr, 'property'):
            continue
        if hasattr(obj, 'formfields') and prop in obj.formfields.keys() and \
                obj.formfields[prop].get('skip', False) == True:
            # This property should be skipped for the interface
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
        v = getattr(inst, c)
        if isinstance(v, list):
            v = ",".join([v2 and str(v2) or None for v2 in v])
        if v is None:
            v = ''
        # else:
        #    v=v and wtforms.utils.intget(v) or (v and str(v) or None)
        values.append((c, v))
    values.append(('id', inst.id))
    return OrderedDict(values)


def get_simple_columns(obj):
    """
    Retrieves the 'normal' fields for an SQLAlchemy object. This excludes
    any fields defined through relationship attributes.
    """

    for attr in get_data_attributes(obj):
        if isinstance(attr.property, ColumnProperty):
            # this is a normal column property
            # map the column to it's form equivalent
            for c in attr.property.columns:
                if len(c.foreign_keys) > 0:
                    # skip foreign keys
                    continue
                if c.primary_key:
                    # skip the primary key
                    continue
                yield c


def get_relation_attributes(obj):
    """
    Gets all one-to-many relationship attributes for an SQLAlchemy object.
    """

    for attr in get_data_attributes(obj):
        if isinstance(attr.property, RelationshipProperty):
            if attr.property.uselist is True:
                # skip the property if it is on the Many side of One-to-Many
                # or Many-to-Many relationships
                continue
            yield attr


def get_multi_relation_attributes(obj):
    """
    Gets all many-to-many relationship attributes for an SQLAlchemy object.
    """

    for attr in get_data_attributes(obj):
        prop = attr.property
        if isinstance(prop, RelationshipProperty) and prop.backref is not None:
            target = prop.mapper.entity
            target_prop = getattr(target, prop.backref).property
            if prop.uselist is True and target_prop.uselist is True:
                # this is a Many-to-Many relationship
                yield attr


def get_primary_keys(obj):
    """
    Gets all primary keys for an SQLAlchemy object.
    """

    return [c.name for c in inspect(obj).primary_key]


def get_fields(obj, orm):
    """
    Gets wtform fields for all attributes of an SQLAlchemy object.
    It maps SQLAlchemy attributes to wtform fields, taking relationship
    attributes (one-to-many and many-to-many) into account.
    """
    datasetname = obj.__module__.split('.')[-1]
    fields = OrderedDict()
    for attr in get_relation_attributes(obj):
        # turn foreign keys into dropdowns with the id as value
        # and the column "name" as description
        target = attr.property.mapper.entity
        values = orm.query(target).all()
        fname = getattr(target, 'pretty_name', attr.key)
        args = {'datasetname': datasetname, 'clsname': fname}
        data_url = url_for('.class_index', **args)
        new_url = url_for('.newclass', **args)
        fields[fname] = {
            'widget': wtforms.SelectField,
            'label': fname,
            'args': [],
            'html_attributes': {'data-values_url': '%s' % data_url},
            'kwargs': {
                'choices': [(v.id, str(v)) for v in values],
                'coerce': int,
                'description':
                    "<a class='addlink' href='%s'>Add %s</a>" %
                    (new_url, fname),
                }}
    for attr in get_multi_relation_attributes(obj):
        # turn foreign keys for many-to-many relations into dropdowns
        # with the id as value and the column "name" as description
        # the dropdown should allow multiple values
        target = attr.property.mapper.entity
        values = orm.query(target).all()
        fname = getattr(target, 'pretty_name', target.__name__)
        args = {'datasetname': unicode(datasetname), 'clsname': unicode(fname)}
        data_url = url_for('.class_index', **args)
        new_url = url_for('.newclass', **args)
        fields[attr.key] = {
            'widget': wtforms.SelectMultipleField,
            'label': attr.key,
            'args': [],
            'html_attributes': {'data-values_url': '%s' % data_url},
            'kwargs': {
                'choices': [(v.id, str(v)) for v in values],
                'coerce': int,
                'description':
                    "<a class='addlink' href='%s'>Add %s</a>" %
                    (new_url, fname),
                }}
    for c in get_simple_columns(obj):
        # map the form widgets by the SQLAlchemy column type
        fields[c.name] = map_column_type(c)

    if hasattr(obj, 'formfields'):
        # adjust the widgets by the arguments defined in the model
        for k, v in obj.formfields.items():
            field = fields.get(k, {})
            if v.get('skip', False) is True:
                continue
            args = v.get('args', field.get('args', []))
            kwargs = field.get('kwargs', {})
            kwargs.update(v.get('kwargs', {}))
            widget = v.get('widget', field.get('widget'))
            valuefunc = v.get('valuefunc', field.get('valuefunc', None))
            if widget != wtforms.SelectField and \
                    widget != wtforms.SelectMultipleField:
                if 'choices' in kwargs.keys():
                    del(kwargs['choices'])
                if 'coerce' in kwargs.keys():
                    del(kwargs['coerce'])
            html_attributes = v.get('html_attributes',
                                    field.get('html_attributes', {}))
            fields[k] = {'label': k, 'widget': widget,
                         'args': args, 'kwargs': kwargs,
                         'html_attributes': html_attributes}
            if valuefunc is not None:
                fields[k]['valuefunc'] = valuefunc

    for k, v in fields.items():
        # instantiate the widgets
        fields[k] = v['widget'](v['label'], v['args'], **v['kwargs'])
        fields[k].html_attributes = v['html_attributes']
        if 'valuefunc' in v.keys():
            fields[k].valuefunc = v['valuefunc']
    fields.values()[0].html_attributes['autoFocus'] = True

    return fields
