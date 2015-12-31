from flask import Blueprint, jsonify, request, render_template, g, flash
from flask import redirect, url_for, Response
import json
from sqlalchemy import or_, and_
from util import get_object, get_colnames, get_values, json_desired
from util import get_fields, get_primary_keys, store_values, get_form_values
import wtforms
from werkzeug.datastructures import MultiDict, ImmutableMultiDict
from biodata import model

basebp = Blueprint('/', 'BaseBlueprint', template_folder='templates')


@basebp.route('/')
def index():
    """
    The initial page with the selection of the dataset.

    """
    datasets = [d.__name__.split('.')[-1] for d in model.datasets]
    retval = {'datasets': datasets}
    return render_template('index.html', **retval)


@basebp.route('/<datasetname>/<clsname>/delete/<int:id>')
def delete(datasetname, clsname, id):
    """
    Delete an sqlalchemy instance (row) from the database.

    :param datasetname: The name of the dataset to delete an the instance from.
    :param clsname: The name of the class to delete an instance from.
    :param id: The id of the instance to delete from the database.
    """
    obj = get_object(datasetname, clsname)
    inst = g.db.session.query(obj).get(id)
    g.db.session.delete(inst)
    del inst
    g.db.session.commit()
    return jsonify({'success': True})


@basebp.route('/<datasetname>/<clsname>/list')
@basebp.route('/<datasetname>/<clsname>/')
def class_index(datasetname, clsname):
    """
    Show a list of all instances of the object/dataset combination.

    :param datasetname: The name of the dataset to fetch the instances for.
    :param clsname: The name of the class to fetch the instances for.
    """
    params = []
    obj = get_object(datasetname, clsname)
    for k in request.args.keys():
        # Get query parameters from the query string
        v = request.args.getlist(k)
        if isinstance(v, list) and len(v) > 1:
            v = or_(*[getattr(obj, k) == v1 for v1 in v])
        elif isinstance(v, list):
            v = getattr(obj, k) == v[0]
        params.append(v)

    instances = g.db.session.query(obj)  # Start building the query

    if params:
        # Filter the instances if we got parameters in the querystring
        instances = instances.filter(and_(*params))

    if hasattr(obj, '_sort'):
        # Sort the instances if a sort key was specified in the model
        sortfields = []
        for field, desc in obj._sort:
            sortfield = getattr(obj, field)
            if desc:
                sortfield = sortfield.desc()
            sortfields.append(sortfield)
        instances = instances.order_by(*sortfields)

    instances = instances.all()  # Get all instances
    if json_desired():
        data = [(s.id, str(s)) for s in instances]
        return Response(json.dumps(data),  mimetype='application/json')
        # return jsonify(data)
    else:
        retval = {
          'instances': [get_values(i) for i in instances],
          'fields': get_colnames(obj),
          'name': obj.__name__}
        return render_template('instance_list.html', **retval)


@basebp.route("/<datasetname>/<clsname>/edit/<int:id>",
              methods=["GET", "POST"])
def edit(datasetname, clsname, id):
    """
    Edit one specific object.

    :param datasetname: The name of the dataset to edit the instance for.
    :param clsname: The name of the class to edit the instance for.
    :param id: The id of the instance to edit.
    """
    obj = get_object(datasetname, clsname)
    inst = g.db.session.query(obj).get(id)
    args = {'datasetname': datasetname,
            'clsname': clsname,
            'id': id}
    action = url_for('.edit', **args)
    retval = {'id': '%s' % clsname,
              'title': 'New %s' % clsname.capitalize(),
              'action': action}
    if inst is None:
        fields = {}
        flash("%s with id %s not found" % (clsname, id))
        retval['form'] = get_form(obj, g.db.session)
        return render_template('form.html', **retval)

    fields = get_form_values(inst)
    if request.method == "GET":
        retval['form'] = get_form(obj, g.db.session, values=fields)
        return render_template('form.html', **retval)
    else:
        form = get_form(obj, g.db.session, data=request.form)
        return save(obj, g.db.session, form)


@basebp.route("/<datasetname>/<clsname>/<int:id>")
def show(datasetname, clsname, id):
    """
    Show one specific object.

    :param datasetname: The name of the dataset to fetch the instance for.
    :param clsname: The name of the class to fetch the instance for.
    :param id: The id of the instance to fetch.
    """
    cls = get_object(datasetname, clsname)
    inst = g.db.session.query(cls).get(id)
    if inst is None:
        fields = {}
        flash("%s with id %s not found" % (clsname, id))
    else:
        fields = get_values(inst)
    retval = {'classname': clsname, 'id': id, 'fields': fields}
    return render_template('show.html', **retval)


@basebp.route("/<datasetname>/new", methods=["POST", "GET"])
def newsample(datasetname):
    retval = {}
    return render_template('new.html', **retval)


@basebp.route("/<datasetname>/edit/<int:id>", methods=["POST", "GET"])
def editsample(datasetname, id):
    retval = {'sample_id': id}
    return render_template('new.html', **retval)


@basebp.route("/<datasetname>/<clsname>/new", methods=["POST", "GET"])
def newclass(datasetname, clsname):
    obj = get_object(datasetname, clsname)
    if request.method == "GET":
        args = {'datasetname': datasetname,
                'clsname': clsname}
        action = url_for('.newclass', **args)
        form = get_form(obj, g.db.session, data=request.args.copy())
        retval = {'id': '%s' % clsname,
                  'title': 'New %s' % clsname.capitalize(),
                  'form': form,
                  'action': action}
        return render_template('form.html', **retval)
    else:
        form = get_form(obj, g.db.session, data=request.form)
        return save(obj, g.db.session, form)


def get_form(obj, orm, data=None, values={}):
    """
    Get the form for a new SQLAlchemy object.

    :param obj: The SQLAlchemy object to get the form for.
    :param orm: The SQLALchemy session to use.
    :param data: The a request-data wrapper object with which the form should
        be filled. Typically a Werkzeug/Django/WebOb MultiDict.
    :param inst: The SQLAlchemy instance to use to fill the form with.
    """
    fields = get_fields(obj, orm)
    fields['redirect'] = wtforms.HiddenField('redirect')
    for pkey in get_primary_keys(obj):
        fields[pkey] = wtforms.HiddenField(pkey)

    class formclass(wtforms.Form):
        pass

    for name, field in fields.items():
        setattr(formclass, name, field)
    if data is None and values == {}:
        data = MultiDict()
    elif isinstance(data, ImmutableMultiDict):
        data = data.copy()
    if data is not None:
        data['redirect'] = data.get('redirect', 'list')
    else:
        values['redirect'] = values.get('redirect', 'list')
    form = formclass(formdata=data, **values)

    for name, field in fields.items():
        # set html_attributes again as they got lost by formclass(...)
        html_attributes = getattr(field, 'html_attributes', {})
        valuefunc = getattr(field, 'valuefunc', {})
        formfield = getattr(form, name)
        formfield.html_attributes = html_attributes
        formfield.valuefunc = valuefunc

    return form


def save(obj, orm, form):
    """
    Save an SQLAlchemy object after form submission.

    :param obj: The SQLAlchemy object to save.
    :param orm: The SQLAlchemy session to save the object to.
    :param form: The :class:`wtforms.Form` form to get the values from.
    """

    clsname = request.view_args['clsname']
    datasetname = request.view_args['datasetname']
    args = {'datasetname': datasetname,
            'clsname': clsname}
    action = url_for('.newclass', **args)
    if not form.validate():
        # Validation failed. Back to the form with the error message
        retval = {'id': "%s_%s" % (datasetname, clsname),
                  'title': "New %s" % clsname.capitalize(),
                  'form': form,
                  'action': action}
        return render_template('form.html', **retval)

    inst = store_values(obj, orm, form.data)
    # handle the resulting redirection.
    if 'x-requested-with' in [k.lower() for k in request.headers.keys()]:
        # we're dealing with an ajax request
        if form.redirect.data == 'form':
            # back to the form with the same values
            # for the hidden (reference id) and dropdown fields
            source = []
            for field in form:
                if isinstance(field, wtforms.SelectField)\
                        or isinstance(field, wtforms.SelectMultipleField)\
                        or isinstance(field, wtforms.HiddenField):
                    source.append((field.name, field.data))
            source = MultiDict(source)
            form = get_form(obj, orm, data=source)
            retval = {'form': form,
                      'id': "%s" % clsname,
                      'title': 'New %s' % clsname.capitalize(),
                      'action': action}
            return render_template('form.html', **retval)
        else:
            # show the added item
            # return redirect('/%s'%inst.id)
            args = {'id': inst.id,
                    'datasetname': datasetname,
                    'clsname': clsname
                    }
            return redirect(url_for('.show', **args))
    elif form.redirect.data == u'form':
        # redirect to the form again, empty values in the form first
        form = get_form(obj, orm, data=MultiDict({'redirect': 'form'}))
        retval = {'form': form,
                  'id': "%s" % clsname,
                  'title': 'New %s' % clsname.capitalize(),
                  'action': action}
        return render_template('form.html', **retval)
    else:
        # redirect to the list page
        args = {'datasetname': datasetname,
                'clsname': clsname
                }
        return redirect(url_for('.class_index', **args))
