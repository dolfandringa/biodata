import web
from web import form
from model import *
from _base import BaseController, BaseShowController, BaseListController


render = web.template.render('templates/')

def getApplication(orm_cls):
    urls = (
        "/", "list",
        "/new", "new",
        "/(.+)", "show"
    )

    class list(BaseListController):
        ORM_CLS = orm_cls


    class show(BaseShowController):
        ORM_CLS = orm_cls


    class new(BaseController):
        ID = orm_cls.__name__.lower()
        TITLE = 'New %s'%orm_cls.__name__
        ORM_CLS = orm_cls

    return web.application(urls, locals())
