from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson


class TestViews(TestCase):

    def test_model_select(self):
        response = self.client.get(reverse('models'))
        assert response.status_code == 200
        models = simplejson.loads(response.content)
        assert models == {"models": [["contenttypes", "contenttype"], ["auth", "permission"], \
                                    ["auth", "group"], ["auth", "user"], ["auth", "message"], \
                                    ["sessions", "session"], ["sites", "site"]]}

    def test_model_details(self):
        response = self.client.get(reverse('model.details', kwargs={'app_label':'auth', \
                                                                    'model_name':'user'}))
        assert response.status_code == 200
        details = simplejson.loads(response.content)
        assert details == {"fields": [u'id', u'username', u'first_name', u'last_name', u'email',
                                      u'password', u'is_staff', u'is_active', u'is_superuser',
                                      u'last_login', u'date_joined'],
                          "managers": ["objects"],
                          "related_fields": [[u'groups', u'auth', u'group'],
                                             [u'user_permissions', u'auth', u'permission']]
                          }

        response = self.client.get(reverse('model.details', kwargs={'app_label':'auth', \
                                                                    'model_name':'permission'}))
        assert response.status_code == 200
        details = simplejson.loads(response.content)
        assert details == {"fields": [u'id', u'name', u'codename'],
                          "managers": ["objects"],
                          "related_fields": [[u'content_type', u'contenttypes', u'contenttype']]
                          }

    def test_queryset_analyzer(self):
        queries = (dict(app='auth', model='user', filters=[{'username__contains':'e'}]),
                   dict(app='auth', model='user', excludes=[{'username__contains':'e'}]),
                   )
        for query in queries:
            response = self.client.post(reverse('analyze.queryset'),
                                        dict(query=simplejson.dumps(query)))
            assert response.status_code == 200
