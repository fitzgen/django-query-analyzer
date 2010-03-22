from django.conf import settings
from django.db import connections
from django.db.backends.sqlite3.base import DatabaseWrapper as sqlite3
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper as postgresql_psycopg2
from django.db.models import get_model as django_get_model
from django.db.models import get_models as django_get_models
from django.db.models.fields.related import ForeignKey

from itertools import chain
from query_analyzer.decorators import json_view

try:
    from pygments import highlight
    from pygments.lexers import PythonLexer, SqlLexer
    from pygments.formatters import HtmlFormatter
    has_pygments = True
except ImportError:
    has_pygments = False

class InvalidSQLError(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)

class Analyzer(object):
    def explain(self, connection):
        cursor = connection.cursor()
        if isinstance(connection, postgresql_psycopg2):
            explain_sql = "EXPLAIN %s" % self.sql
        else:
            explain_sql = "EXPLAIN %sPLAN %s" % (isinstance(connection, sqlite3) and "QUERY " or "", self.sql)
        try:
            cursor.execute(explain_sql, self.params)
            explain_headers = [d[0] for d in cursor.description]
            explain_result = cursor.fetchall()
            sql = connection.ops.last_executed_query(cursor, self.sql, self.params),
        finally:
            cursor.close()
        return explain_headers, explain_result, sql

class AnalyzeSQL(Analyzer):
    def __init__(self, sql, params):
        self.sql = sql
        self.params = params
        
    def __call__(self):
        if not self.sql:
            context = {}
        else:
            if self.sql.lower().strip().startswith('select'):
                if self.params:
                    self.params = simplejson.loads(self.params)
                else:
                    self.params = {}

                connection = connections['default']
                cursor = connection.cursor()
                try:
                    cursor.execute(sql, params)
                    select_headers = [d[0] for d in cursor.description]
                    select_result = cursor.fetchall()
                finally:
                    cursor.close()

                explain_headers, explain_result, sql_result = _explain(connection)
                # not sure what to do with sql_result in this case...
                context = {
                    'select_result': select_result,
                    'explain_result': explain_result,
                    'sql': sql,
                    'duration': request.GET.get('duration', 0.0),
                    'select_headers': select_headers,
                    'explain_headers': explain_headers,
                }
            else:
                raise InvalidSQLError("Only 'select' queries are allowed.")

class AnalyzePython(Analyzer):
    def __init__(self, model, python):
        self.model = model
        self.manager = model.objects
        self.nice_python = self.python = "%s.objects.%s" % (model.__name__, python.strip())
        if has_pygments:
            self.nice_python = highlight(self.python, PythonLexer(), HtmlFormatter())
        try:
            self.queryset = eval(self.python, dict_models())
        except:
            raise SyntaxError
    
    def __call__(self):
        connection = connections[self.queryset.db]

        self.sql, self.params = self.queryset._as_sql(connection)
        headers, result, sql = self.explain(connection)

        nice_sql = "\n".join(sql)
        if has_pygments:
            nice_sql = highlight(nice_sql, SqlLexer(), HtmlFormatter())
        
        context = {
            'select_result': self.queryset.values_list(),
            'explain_result': result,
            'sql': sql,
            'nice_sql': nice_sql,
            'nice_python': self.nice_python,
            'duration': settings.DEBUG and connection.queries[-1]['time'] or 0.0,
            'select_headers': [f.name for f in self.model._meta.fields], #maybe local_fields is better.
            'explain_headers': headers,
        }
        return context
        

class AnalyzeQueryset(Analyzer):
    def __init__(self, model, manager, filters, excludes):
        self.model = model
        self.manager = manager
        self.filters = filters
        self.excludes = excludes
        self.sql = None
        self.params = None
        
    def __call__(self):
        queryset = manager.all()
    
        for filter in filters:
            queryset = queryset.filter(**filter)
    
        for exclude in excludes:
            queryset = queryset.exclude(**exclude)

        connection = connections[queryset.db]
        
        self.sql, self.params = queryset._as_sql(connection)
        headers, result, sql = _explain(connection)

        context = {
            'select_result': queryset.values_list(),
            'explain_result': result,
            'sql': sql,
            'duration': settings.DEBUG and connection.queries[-1]['time'] or 0.0,
            'select_headers': [f.name for f in model._meta.fields], #maybe local_fields is better.
            'explain_headers': headers,
        }
        return context


def dict_models():
    return dict([(model.__name__, model) for model in django_get_models()])

def list_models():
    return [["%s|%s" % (model._meta.app_label, model._meta.module_name), 
             "%s - %s" % (model._meta.app_label, model._meta.module_name)] 
                for model in django_get_models() ]

def get_model(model_string):
    return django_get_model(*model_string.split("|"))
        
def detail_model(model):
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
    