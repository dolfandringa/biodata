from flask import Blueprint, jsonify, request, render_template, g, flash
from biodata.model import datasets
from sqlalchemy import or_, and_
from util import *

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


@basebp.route("/<datasetname>/<clsname>/new")
def new(datasetname, clsname):
    pass
