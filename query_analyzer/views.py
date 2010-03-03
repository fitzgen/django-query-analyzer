from django.conf import settings
from django.db import connection
from django.db.models import get_model
from django.db.models import get_models
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.utils.hashcompat import sha_constructor
from itertools import chain
from query_analyzer.decorators import json_view


class InvalidSQLError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def analyze(request):
    sql = request.GET.get('sql', '')
    params = request.GET.get('params', '')
    #hash = sha_constructor(settings.SECRET_KEY + sql + params).hexdigest()
    #if hash != request.GET.get('hash', ''):
        #return HttpResponseBadRequest('Tamper alert') # SQL Tampering alert
    if sql.lower().strip().startswith('select'):
        if params:
            params = simplejson.loads(params)
        cursor = connection.cursor()

        # SELECT
        cursor.execute(sql, params)
        select_headers = [d[0] for d in cursor.description]
        select_result = cursor.fetchall()

        # EXPLAIN
        if settings.DATABASE_ENGINE == "sqlite3":
            cursor.execute("EXPLAIN QUERY PLAN %s" % (sql,), params)
        else:
            cursor.execute("EXPLAIN %s" % (sql,), params)
        explain_headers = [d[0] for d in cursor.description]
        explain_result = cursor.fetchall()

        cursor.close()

        context = {
            'select_result': select_result,
            'explain_result': explain_result,
            'sql': cursor.db.ops.last_executed_query(cursor, sql, params),
            'duration': request.GET.get('duration', 0.0),
            'select_headers': select_headers,
            'explain_headers': explain_headers,
        }
        return render_to_response('query_analyzer/analyze.html', context)
    raise InvalidSQLError("Only 'select' queries are allowed.")


@json_view
def model_select(request):
    content = {
        'models': [(model._meta.app_label, model._meta.module_name) for model in get_models()],
    }
    return content


@json_view
def model_details(request, app_label, model_name):
    model = get_model(app_label, model_name)
    content = {
        'managers': [(id, name) for id, name, manager in chain(model._meta.concrete_managers,
                                                               model._meta.abstract_managers)],
        'fields': model._meta.get_all_field_names(),
        'related_fields': [rel.get_accessor_name() for rel in model._meta.get_all_related_objects()],
    }
    return content
