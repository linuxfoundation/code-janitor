import os, re, urllib

from django.conf import settings
from django.shortcuts import render_to_response
from django import forms
from django.http import HttpResponse, HttpResponseRedirect

from janitor.site_settings import gui_name, gui_version
from janitor.search.models import *

# Form classes

class SearchForm(forms.Form):
    path = forms.CharField(max_length=100)

class KeywordForm(forms.Form):
    wordlist = forms.CharField(widget=forms.Textarea)

def scan(request):
    nokeywords = ''
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = Search.do(form.cleaned_data["path"])
            return HttpResponseRedirect("/search/results/%d" % search.id)
    else:
        form = SearchForm()

    # issue a note is no keywords defined
    keywordcount = Keyword.objects.count()
    if keywordcount == 0:
        nokeywords = 'You should define keywords first on the <a href="search/keywords">Keywords</a> tab.'

    return render_to_response("search/scan.html", { "form": form,
                                                    "nokeywords": nokeywords,
                                                    "tab_scan": True })

def results(request, result_id=-1):
    if result_id < 0:
        results = Search.objects.all()
        return render_to_response("search/result_list.html", 
                                  { 'searches': results,
                                    'tab_results': True })
    else:
        result = Search.objects.get(id=result_id)
        searched = result.searchitem_set.filter(skipped=False)
        not_searched = result.searchitem_set.filter(skipped=True)
        return render_to_response("search/result_detail.html",
                                  { 'search': result,
                                    'searched': searched,
                                    'not_searched': not_searched,
                                    'tab_results': True })

def keywords(request):
    errmsg = ''
    errlist = []
    if request.method == "POST":
        mode = urllib.unquote(request.POST.get('submit'))

        if re.search("^Add", mode):   
            form = KeywordForm(request.POST) # A form bound to the POST data
            # request to add data
            if form.is_valid(): # All validation rules pass
                wl = form.cleaned_data['wordlist']
                words = wl.split("\n")
                # remove dups
                words = list(set(words))
                print words
                for word in words:
                    word = word.rstrip("\r")
                    # no empty strings
                    if word:
                        kw = Keyword(keyword = word)
                        try:
                            kw.save()
                        except:
                            errlist.append(str(word))
                
                if errlist:
                    errmsg = "<b>Warning:</b> did not add duplicate keyword(s): " + str(errlist)
                    
        if re.search("^Delete", mode): 
            # delete request
            keywordlist = request.POST.get('keywordlist', '')
            if keywordlist != '':
                delete_records(Keyword, keywordlist)

    form = KeywordForm()
    latest_keyword_list = Keyword.objects.all().order_by('keyword')

    return render_to_response("search/keywords.html", { "form": form,
                                                    "errmsg": errmsg,
                                                    "latest_keyword_list": latest_keyword_list,
                                                    "tab_keywords": True })

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

# this does not have a corresponding dirlist.html
# this is dynamic filetree content fed to jqueryFileTree for the test.html file/dir selection
# script for jqueryFileTree points to /linkage/dirlist/
def dirlist(request):
    # filter out some directories that aren't useful from "/"
    not_wanted = [ '/proc', '/dev', '/sys', '/initrd' ]
    r=['<ul class="jqueryFileTree" style="display: none;">']
    try:
        d=urllib.unquote(request.POST.get('dir'))
        content = os.listdir(d)
        # slows things a little, but looks more like 'ls'
        for f in sorted(content, key=unicode.lower):
            ff=os.path.join(d,f)
            if ff not in not_wanted and f != 'lost+found':
                if os.path.isdir(ff): 
                    r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (ff,f))
                else:
                    e=os.path.splitext(f)[1][1:] # get .ext and remove dot
                    r.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (e,ff,f))
        r.append('</ul>')
    except Exception,e:
        r.append('Could not load directory: %s' % str(e))
    r.append('</ul>')
    return HttpResponse(''.join(r))

## utility functions

# delete table records requested by id from one of the input forms
def delete_records(table, rlist):
            
    records = rlist.split(",")

    for record in records:
        if record != '':
            q = table.objects.filter(id = record)
            q.delete()

