from django.conf.urls.defaults import *
from janitor.search.models import *

urlpatterns = patterns('',
    url(r'documentation/$', 'janitor.search.views.documentation'),
    url(r'scan/$', 'janitor.search.views.scan'),
    url(r'results/(?P<result_id>\d+)$', 'janitor.search.views.results',
        name="results_detail"),
    url(r'results/$', 'janitor.search.views.results'),
)
