from django.conf.urls.defaults import *

urlpatterns = patterns('query_analyzer.views',
    url(r'^analyze/$', 'analyze'),
)

