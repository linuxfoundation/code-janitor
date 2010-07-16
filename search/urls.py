from django.conf.urls.defaults import *
from janitor.search.models import *

urlpatterns = patterns('',
    url(r'^$', 'janitor.search.views.index'),
    url(r'^taskstatus/$', 'janitor.search.views.taskstatus'),
    url(r'^documentation/$', 'janitor.search.views.documentation'),
    url(r'^scan/$', 'janitor.search.views.scan'),
    url(r'^keywords/$', 'janitor.search.views.keywords'),
    url(r'^dirlist/$', 'janitor.search.views.dirlist'),
    url(r'^results/(?P<result_id>\d+)$', 'janitor.search.views.results',
        name="results_detail"),
    url(r'^results/$', 'janitor.search.views.results'),
)
