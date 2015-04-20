import web
from web import form
from _base import BaseController, BaseShowController, BaseListController
from _base import BaseDeleteController


def getApplication(orm_cls):

    class lst(BaseListController):
        ORM_CLS = orm_cls


    class show(BaseShowController):
        ORM_CLS = orm_cls


    class deletectl(BaseDeleteController):
        ORM_CLS = orm_cls


    class new(BaseController):
        ID = orm_cls.__name__.lower()
        TITLE = 'New %s'%orm_cls.__name__
        ORM_CLS = orm_cls

    urls = (
        "/", lst,
        "/new", new,
        "/([0-9]+)", show,
        "/delete", deletectl
    )

    return web.application(urls, locals())
