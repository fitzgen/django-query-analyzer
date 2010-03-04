from django.conf import settings
from django.db import connections
from django.db.backends.sqlite3.base import DatabaseWrapper as sqlite3
from django.db.models import get_model
from django.db.models import get_models
from django.db.models.fields.related import ForeignKey
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
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
    if not sql:
        context = {}
    else:
        if sql.lower().strip().startswith('select'):
            if params:
                params = simplejson.loads(params)
            else:
                params = {}

            connection = connections['default']
            cursor = connection.cursor()
            try:
                cursor.execute(sql, params)
                select_headers = [d[0] for d in cursor.description]
                select_result = cursor.fetchall()
            finally:
                cursor.close()

            explain_headers, explain_result, sql_result = _explain(connection, sql, params)

            context = {
                'select_result': select_result,
                'explain_result': explain_result,
                'sql': sql_result,
                'duration': request.GET.get('duration', 0.0),
                'select_headers': select_headers,
                'explain_headers': explain_headers,
            }
        else:
            raise InvalidSQLError("Only 'select' queries are allowed.")

    context["ADMIN_MEDIA_PREFIX"] = settings.ADMIN_MEDIA_PREFIX

    return render_to_response('query_analyzer/analyze.html',
                              context,
                              context_instance=RequestContext(request))


def analyze_queryset(request):
    query = simplejson.loads(request.POST.get('query', '{}'))
    model = get_model(query.get('app'), query.get('model'))
    manager = getattr(model, query.get('manager', '_default_manager'))

    queryset = manager.all()
    filters = query.get('filters', [])
    for filter in filters:
        queryset = queryset.filter(**filter)
    excludes = query.get('excludes', [])
    for exclude in excludes:
        queryset = queryset.exclude(**exclude)

    connection = connections[queryset.db]
    headers, result, sql = _explain(connection, *queryset._as_sql(connection))

    context = {
        'select_result': queryset.values_list(),
        'explain_result': result,
        'sql': sql,
        'duration': settings.DEBUG and connection.queries[-1]['time'] or 0.0,
        'select_headers': [f.name for f in model._meta.fields], #maybe local_fields is better.
        'explain_headers': headers,
    }
    return render_to_response('query_analyzer/analyze.html',
                              context,
                              context_instance=RequestContext(request))

def _explain(connection, sql, params):
    cursor = connection.cursor()
    explain = "EXPLAIN %sPLAN %s" % (isinstance(connection, sqlite3) and "QUERY " or "", sql)
    try:
        cursor.execute(explain, params)
        explain_headers = [d[0] for d in cursor.description]
        explain_result = cursor.fetchall()
        sql = connection.ops.last_executed_query(cursor, sql, params),
    finally:
        cursor.close()
    return explain_headers, explain_result, sql

@json_view
def model_select(request):
    content = {
        'models': [(model._meta.app_label, model._meta.module_name) for model in get_models()],
    }
    return content


@json_view
def model_details(request, app_label, model_name):
    model = get_model(app_label, model_name)
    managers = [name for id, name, manager in chain(model._meta.concrete_managers,
                                                    model._meta.abstract_managers)
                if not name.startswith('_')]
    fields = [field.name for field in model._meta.local_fields
              if not isinstance(field, ForeignKey)]
    # handle fields with relation (fk, m2m)
    related_fields = [field for field in model._meta.local_fields
                      if isinstance(field, ForeignKey)]
    related_fields = [(field.name, field.rel.to._meta.app_label, field.rel.to._meta.module_name) \
                      for field in chain(model._meta.many_to_many, related_fields)]
    return dict(managers=managers, fields=fields, related_fields=related_fields)


# dragables
'filter', 'exclude'
# radio button
'count', 'select_related', 'exists'
# checkboxes
'reverse'