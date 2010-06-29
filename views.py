# Views not associated with a Django app.  This is mostly for the toplevel
# index page.

from django.shortcuts import render_to_response

def toplevel(request):
    return render_to_response("index.html")
