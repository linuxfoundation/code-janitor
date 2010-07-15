import os

from django.conf import settings
from django.shortcuts import render_to_response
from django import forms
from django.http import HttpResponse, HttpResponseRedirect

from janitor.site_settings import gui_name, gui_version
from janitor.search.models import *
from janitor.util import task

# Form classes

class SearchForm(forms.Form):
    path = forms.CharField(max_length=100)

def taskstatus(request):
    tm = task.TaskManager()
    return HttpResponse(tm.read_status())

def scan(request):
    if request.method == "POST":
        tm = task.TaskManager()
        form = SearchForm(request.POST)
        if form.is_valid() and not tm.is_running():
            search = Search(top_path=form.cleaned_data["path"])
            search.save()
            tm.start(search.do)
            return HttpResponseRedirect("/search/results/%d" % search.id)
    else:
        form = SearchForm()

    return render_to_response("search/scan.html", { "form": form,
                                                    "tab_scan": True })

def results(request, result_id=-1):
    if result_id < 0:
        results = Search.objects.all()
        return render_to_response("search/result_list.html", 
                                  { 'searches': results,
                                    'tab_results': True })
    else:
        result = Search.objects.get(id=result_id)
        return render_to_response("search/result_detail.html",
                                  { 'search': result,
                                    'tab_results': True })

def documentation(request):
    # Read the standalone docs, and reformat for the gui
    docs = ''
    status = 0

    try:
        f = open(settings.STATIC_DOC_ROOT + "/docs/index.html", 'r')

    except:
        # docs are created yet, try to do it
        status = os.system("cd " + settings.STATIC_DOC_ROOT + "/docs && make")
        if status != 0:
            status = os.system("cd " + settings.STATIC_DOC_ROOT + "/docs && ./text-docs-to-html > index.html.addons")
            if status == 0:
                status = os.system("cd " + settings.STATIC_DOC_ROOT + "/docs && cat index.html.base index.html.addons index.html.footer > index.html")
            else:
                docs = "<b>Error, no index.html in compliance/media/docs.</b><br>"
                docs += "If working with a git checkout or tarball, please type 'make' in the top level directory."

    # something worked above
    if not docs:
        f = open(settings.STATIC_DOC_ROOT + "/docs/index.html", 'r')
        doc_index = []
        for line in f:
            #replace the div styles for embedded use
            line = line.replace('<div id="lside">', '<div id="lside_e">')
            line = line.replace('<div id="main">', '<div id="main_e">')
            doc_index.append(line)
        f.close()
    
        # drop the first 11 lines
        docs = ''.join(doc_index[11:])

    return render_to_response('search/documentation.html', 
                              {'name': gui_name, 
                               'version': gui_version, 
                               'gui_docs': docs })

