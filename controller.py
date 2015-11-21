from flask import Blueprint, jsonify, request, render_template, g, flash
from flask import redirect
from biodata.model import datasets
from sqlalchemy import or_, and_
from util import *
import wtforms

basebp = Blueprint('/', 'BaseBlueprint', template_folder='templates')


@basebp.route('/<datasetname>/<clsname>/delete/<int:id>', methods=["POST"])
def delete(datasetname, clsname, id):
    obj = get_object(datasetname, clsname)
    inst = g.db.session.query(obj).get(id)
    g.db.session.delete(inst)
    del inst
    return jsonify({'success': True})


@basebp.route('/<datasetname>/<clsname>/')
def index(datasetname, clsname):
    params = []
    obj = get_object(datasetname, clsname)
    for k in request.args.keys():
        v = request.args.getlist(k)
        if isinstance(v, list) and len(v) > 1:
            v = or_(*[getattr(obj, k) == v1 for v1 in v])
        elif isinstance(v, list):
            v = getattr(obj, k) == v[0]
        params.append(v)
    if params:
        instances = g.db.session.query(obj).filter(and_(*params)).all()
    else:
        instances = g.db.session.query(obj).all()
    if json_desired():
        return jsonify([(s.id, str(s)) for s in instances])
    else:
        retval = {
          'instances': [get_values(i) for i in instances],
          'fields': get_colnames(obj),
          'name': obj.__name__}
        return render_template('instance_list.html', **retval)


@basebp.route("/<datasetname>/<clsname>/edit/<int:id>")
def edit(datasetname, clsname, id):
    pass


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
    pass


@basebp.route("/<datasetname>/<clsname>/new", methods=["POST", "GET"])
def newclass(datasetname, clsname):
    obj = get_object(datasetname, clsname)
    if request.method == "GET":
        form = get_form(obj, g.db.session)
        retval = {'id': '%s_%s' % (datasetname, clsname),
                  'title': '%s' % clsname,
                  'form': form}
        return render_template('form.html', **retval)
    else:
        form = get_form(obj, g.db.session, data=request.form)
        save(obj, g.db.session, form)


def get_form(obj, orm, data=None, datadict=None):
    """
    Get the form for a new SQLAlchemy object.

    :param obj: The SQLAlchemy object to get the form for.
    :param orm: The SQLALchemy session to use.
    :param data: The a request-data wrapper object with which the form should
        be filled. Typically a Werkzeug/Django/WebOb MultiDict.
    :param datadict: A dictionary type object with data for filling the form.
    """
    fields = get_fields(obj, orm)
    fields['redirect'] = wtforms.HiddenField('redirect')
    for pkey in get_primary_keys(obj):
        fields[pkey] = wtforms.HiddenField(pkey)

    class formclass(wtforms.Form):
        pass
    
    for name, field in fields.items():
        setattr(formclass, name, field)

    if data is not None:
        data.redirect = 'list'
    elif datadict is not None:
        datadict['redirect'] = 'list'
    else:
        datadict = {'redirect': 'list'}
    form = formclass(formdata=data, data=datadict)

    for name, field in fields.items():
        # set html_attributes again as they got lost by formclass(...)
        html_attributes = getattr(field, 'html_attributes', {})
        getattr(form, name).html_attributes = html_attributes 

    return form 


def save(obj, orm, form):
    """
    Save an SQLAlchemy object after form submission.

    :param obj: The SQLAlchemy object to save.
    :param orm: The SQLAlchemy session to save the object to.
    :param form: The :class:`wtforms.Form` form to get the values from.
    """

    if not form.validate():
        # Validation failed. Back to the form with the error message
        retval = {'id': "%s_sample" % obj,
                  'title': "Sample",
                  'form': form}
        return render_template('form.html', **retval)

    store_values(obj, orm, form.data)

    # handle the resulting redirection.
    if 'HTTP_X_REQUESTED_WITH' in request.header.keys():
        # we're dealing with an ajax request
        if form.redirect.data == 'form':
            # back to the form with the same values
            # for the hidden (reference id) and dropdown fields
            source = []
            for field in form:
                if isinstance(field, wtforms.SelectField)\
                        or isinstance(field, wtforms.SelectMultiField)\
                        or isinstance(field, wtforms.HiddenField):
                    source.append((field.name, field.data))
            source = dict(source)
            form = get_form(obj, orm, datadict=source)
            retval = {'form': form,
                      'id': "%s_sample" % obj,
                      'title': 'Sample'}
            return render_template('form.html', **retval)
        else:
            # show the added item
            # return redirect('/%s'%inst.id)
            args = {'id': inst.id,
                    'dataset': request.view_args['dataset'],
                    'clsname': request.view_args['clsname']
                    }
            return redirect(url_for('show', **args))
    elif form.redirect.data == 'form':
        # redirect to the form again, empty values in the form first
        form = get_form(obj, orm)
        retval = {'form': form,
                  'id': "%s_sample" % obj,
                  'title': 'Sample'}
        return render_template('form.html', **retval)
    else:
        # redirect to the list page
        args = {'dataset': request.view_args['dataset'],
                'clsname': request.view_args['clsname']
                }
        return redirect(url_for('/', **args))
