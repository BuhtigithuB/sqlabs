# -*- coding: utf-8 -*-
from plugin_tablecheckbox import TableCheckbox
from plugin_solidtable import SOLIDTABLE
from gluon.contrib.populate import populate

db = DAL('sqlite:memory:') 
db.define_table('product', Field('name'))
populate(db.product, 5)

def index():
    
    tablecheckbox = TableCheckbox()
    tablecheckbox.components.insert(0, 
        SELECT('update', 'delete', _name='action', _style='width:70px;',
                requires=IS_IN_SET(['update', 'delete'])))
    
    if tablecheckbox.accepts(request.vars):
        session.flash = 'submitted : selected=%s action=%s' % (
                            tablecheckbox.vars.tablecheckbox, tablecheckbox.vars.action)
        redirect(URL('index'))
    table = SOLIDTABLE(db(db.product.id>0).select(),
                       extracolumns=[tablecheckbox.column()],
                       renderstyle=True)
    return dict(table=table, tablecheckbox=tablecheckbox)
    