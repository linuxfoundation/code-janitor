from django.conf.urls.defaults import *
from janitor.search.models import *

urlpatterns = patterns('',
    url(r'documentation/$', 'janitor.search.views.documentation'),
)
