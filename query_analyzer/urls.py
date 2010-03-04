from django.conf.urls.defaults import *

urlpatterns = patterns('query_analyzer.views',
    url(r'^analyze/$', 'analyze'),
    url(r'^analyze/queryset/$', 'analyze_queryset', name='analyze.queryset'),
    url(r'^models/$', 'model_select', name='models'),
    url(r'^model/(?P<app_label>\w+)/(?P<model_name>\w+)/$', 'model_details', name='model.details'),
)
