# -*- coding: utf-8 -*-
from plugin_comment_box import CommentBox
from gluon.tools import Auth
import unittest
from gluon.contrib.populate import populate

def run_test(TestCase):
    import cStringIO
    stream = cStringIO.StringIO()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
    unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return stream.getvalue()
    
if request.function == 'test':
    db = DAL('sqlite:memory:')
    
auth = Auth(db)
auth.define_tables()
table_target = db.define_table('plugin_comment_box_target', Field('created_on', 'datetime', default=request.now))
comment_box = CommentBox(db)
comment_box.settings.table_comment_name = 'plugin_comment_box_comment'
comment_box.define_tables(str(table_target), auth.settings.table_user_name)

num_users = 3
user_ids = {}
for i in range(1, num_users+1):   
    email = 'user%s@test.com' % i
    user = db(auth.settings.table_user.email==email).select().first()
    user_ids[i] = user and user.id or auth.settings.table_user.insert(email=email)

import datetime
db(table_target.created_on<
    request.now-datetime.timedelta(minutes=10)).delete()
db(comment_box.settings.table_comment.created_on<
    request.now-datetime.timedelta(minutes=10)).delete()
    
for i in range(3-db(table_target.id>0).count()):
    table_target.insert()

def index():
    user_no = int(request.args(0) or 1)
    user_id = user_ids[user_no]
    
    comment_box_form = comment_box.process()
    
    user_chooser = []
    for i in range(1, num_users+1):
        if i == user_no:
            user_chooser.append('user%s' % user_no)
        else:
            user_chooser.append(A('user%s' % i, _href=URL('index', args=i)))
    
    targets = db(table_target.id>0).select()
    _targets = {}
    for target in targets:
        _targets[target.id] = comment_box.element(user_id, target.id)
        
        
    return dict(choose_user=user_chooser,
                targets=_targets,
                hiddens=comment_box_form,
                tests=A('unit test', _href=URL('test')),)
                
    
class TestCommentBox(unittest.TestCase):

    def setUp(self):
        comment_box.settings.table_comment.truncate()
        
    def test_crud(self):
        for target_id in range(1, 3):
            user_id = 1
            comment_box.add_comment(user_id, target_id, 'body_1')
            self.assertEqual(comment_box.comments(target_id).select().first().body, 'body_1')
            
            comment_box.add_comment(user_id, target_id, 'body_2')
            self.assertEqual(comment_box.comments(target_id).count(), 2)
            
            user_id = 2
            comment_box.add_comment(user_id, target_id, 'body_3')
            
            comments = comment_box.comments(target_id).select()
            self.assertEqual(len(comments), 3)
            
            comment_box.remove_comment(user_id, comments[2])
            self.assertEqual(comment_box.comments(target_id).count(), 2)
            
            self.assertRaises(ValueError, comment_box.remove_comment, user_id, comments[1])
            self.assertEqual(comment_box.comments(target_id).count(), 2)
        
    
def test():
    return dict(back=A('back', _href=URL('index')),
                output=CODE(run_test(TestCommentBox)))


