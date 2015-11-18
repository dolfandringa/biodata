from flask import Blueprint, jsonify, request, render_template, g
from biodata.model import datasets
from util import *

basebp = Blueprint('/', 'BaseBlueprint', template_folder='templates')


@basebp.route('/<datasetname>/<clsname>/delete/<int:id>')
def delete(self, datasetname, cls, id):
    obj = get_object(datasetname, clsname)
    inst = g.db.session.query(obj).get(id)
    g.db.session.delete(inst)
    del inst
    return jsonify({'success': True})


@basebp.route('/<datasetname>/<clsname>/')
def list(datasetname, clsname):
    params = request.args
    obj = get_object(datasetname, clsname)
    if params:
            instances = g.db.session.query(obj).filter_by(**params).all()
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


def show():
    pass


def new():
    pass
