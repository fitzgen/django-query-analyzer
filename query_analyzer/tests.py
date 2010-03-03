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
        assert details == {"fields": ["_message_set", "date_joined", "email", "first_name", \
                                      "groups", "id", "is_active", "is_staff", "is_superuser", \
                                      "last_login", "last_name", "password", "user_permissions", \
                                      "username"], \
                          "managers": [[6, "objects"], [9, "_base_manager"]], \
                          "related_fields": [[u'_message_set', u'auth', u'message']]}

