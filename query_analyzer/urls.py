from django.conf.urls.defaults import *

urlpatterns = patterns('query_analyzer.views',
#    url(r'^$', 'analyze'),
    url(r'^basic/$', 'basic_analyze'),    
#    url(r'^api/models/$', 'model_select', name='models'),
#    url(r'^api/model/(?P<app_label>\w+)/(?P<model_name>\w+)/$', 'model_details', name='model.details'),
)
