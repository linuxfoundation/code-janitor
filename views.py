# Views not associated with a Django app.  This is mostly for the toplevel
# index page.

from django.http import HttpResponsePermanentRedirect

def toplevel(request):
    return HttpResponsePermanentRedirect("/search/")
