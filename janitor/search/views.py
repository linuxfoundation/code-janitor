import os, re, urllib

from django.conf import settings
from django.shortcuts import render_to_response
from django import forms
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect

from janitor.site_settings import gui_name, gui_version
from janitor.search.models import *
from janitor.util import task

# Form classes

class SearchForm(forms.Form):
    path = forms.CharField(max_length=100)

class KeywordForm(forms.Form):
    wordlist = forms.CharField(widget=forms.Textarea)

class GroupForm(ModelForm):
    class Meta:
        model = Group

    groups = forms.ChoiceField()
 
    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['groups'].choices = group_choices()

def index(request):
    return HttpResponseRedirect("/search/scan/")

def taskstatus(request):
    tm = task.TaskManager()
    return HttpResponse(tm.read_status())

def scan(request):
    nokeywords = ''
    if request.method == "POST":
        tm = task.TaskManager()
        form = SearchForm(request.POST)
        if form.is_valid() and not tm.is_running():
            grouplist = request.POST.get('grouplist', '')
            if grouplist:
                grouplist=grouplist[:-1]
            search = Search(top_path=form.cleaned_data["path"], group_list=grouplist)
            search.save()
            tm.start(search.do)
            return HttpResponseRedirect("/search/results/%d" % search.id)
    else:
        form = SearchForm()

    # issue a note if no keywords defined
    keywordcount = Keyword.objects.count()
    if keywordcount == 0:
        nokeywords = 'You should define keywords first on the <a href="/search/keywords">Keywords</a> tab.'

    latest_group_list = Group.objects.all().order_by('group')

    return render_to_response("search/scan.html", { "form": form,
                                                    "nokeywords": nokeywords,
                                                    "latest_group_list": latest_group_list,
                                                    "tab_scan": True })

def results(request, result_id=-1):
    if result_id < 0:
        if request.method == "POST":
            mode = urllib.unquote(request.POST.get('submit'))
            if re.search("^Delete", mode): 
                # delete request
                searchlist = request.POST.get('searchlist', '')
                if searchlist != '':
                    delete_records(Search, searchlist)

        results = Search.objects.all().order_by('-start_time')
        return render_to_response("search/result_list.html", 
                                  { 'searches': results,
                                    'tab_results': True })
    else:
        groups = ''
        tm = task.TaskManager()
        result = Search.objects.get(id=result_id)
        if result.group_list != '':
            groups = result.group_list.split(",")
        grouplist = Group.objects.all().filter(id__in=groups)           
        searched = result.searchitem_set.filter(skipped=False)
        searched_list = render_detail(searched, result.top_path)
        not_searched = result.searchitem_set.filter(skipped=True)
        # FIXME still picking up some embedded "u'..'" here, clean it up
        # we want to strip out the top_path anyway
        for s in not_searched:
            s.keyword_found = s.keyword_found.replace("u'", "")
            s.keyword_found = s.keyword_found[:-1]
            s.file_path = s.file_path.replace(result.top_path + "/", "")
            s.keyword_found = s.keyword_found.replace(result.top_path + "/", "")
        return render_to_response("search/result_detail.html",
                                  { 'search': result,
                                    'grouplist': grouplist,
                                    'searched': searched_list,
                                    'not_searched': not_searched,
                                    'task_running': tm.is_running(),
                                    'tab_results': True })

def keywords(request):
    kerrmsg = ''
    kerrlist = []
    gerrmsg = ''
    gadderr = ''
    if request.method == "POST":
        mode = urllib.unquote(request.POST.get('submit'))

        if re.search("^Add", mode) and re.search("Keyword", mode):   
            kform = KeywordForm(request.POST) # A form bound to the POST data
            # request to add data
            if kform.is_valid(): # All validation rules pass
                wl = kform.cleaned_data['wordlist']
                words = wl.split("\n")
                # remove dups
                words = list(set(words))
                for word in words:
                    word = word.rstrip("\r")
                    # no empty strings
                    if word:
                        kw = Keyword(keyword = word)
                        try:
                            kw.save()
                        except:
                            kerrlist.append(str(word))
                
                if kerrlist:
                    kerrmsg = "<b>Warning:</b> did not add duplicate keyword(s): " + str(kerrlist)
                    
        if re.search("^Delete", mode) and re.search("Keyword", mode): 
            # delete request
            keywordlist = request.POST.get('keywordlist', '')
            if keywordlist != '':
                delete_records(Keyword, keywordlist)

        if re.search("^Add Selected", mode) and re.search("Group", mode):   
            kform = KeywordForm(request.POST) # A form bound to the POST data
            # request to add data
            keywordlist = request.POST.get('keywordlist', '')
            group = request.POST.get('groups', '')
            if group != '':
                for k in keywordlist.split(","):
                    if k != '':
                        galready = GroupedKeywords.objects.filter(keyword = k, group = group).count()
                        if not galready:
                            gadd = GroupedKeywords(keyword_id = k, group_id = group)
                            gadd.save()
                        else:
                            gadderr = "<b>Warning:</b> Did not add duplicate group to keyword"          

        if re.search("^Add Group", mode):   
            gform = GroupForm(request.POST) # A form bound to the POST data
            # request to add data
            gadd = request.POST.get('group', '')
            if gadd:
                g = Group(group = gadd)
                try:
                    g.save()
                except:
                    gerrmsg = "<b>Warning:</b> did not add duplicate group: " + gadd

        if re.search("^Delete", mode) and re.search("Groups", mode): 
            # delete request
            grouplist = request.POST.get('grouplist', '')
            if grouplist != '':
                delete_records(Group, grouplist)

    kform = KeywordForm()
    gform = GroupForm()
    latest_keyword_list = Keyword.objects.values('keyword', 'id')
    for k in latest_keyword_list:
        group_id_list = GroupedKeywords.objects.values('group_id').filter(keyword = k['id'])
        groups = []
        for g in group_id_list:
            group_list = Group.objects.values('group').filter(id = g['group_id'])
            for group in group_list:
                groups.append(group['group'])
        groups.sort()
        k['groups'] = ",".join(groups)

    latest_group_list = Group.objects.all().order_by('group')

    return render_to_response("search/keywords.html", { "kform": kform, "gform": gform,
                                                    "kerrmsg": kerrmsg, "gerrmsg": gerrmsg, 
                                                    "gadderr": gadderr,
                                                    "latest_keyword_list": latest_keyword_list,
                                                    "latest_group_list": latest_group_list,
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
                docs = "<b>Error, no index.html in janitor/media/docs.</b><br>"
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

def group_choices():
    # get the available groups to populated the form drop-downs
    groups = Group.objects.all().order_by('group')
    # need a tuple for the drop-down
    choices = []
    # no default
    choices.append(('',''))
    for g in groups:
        choices.append((g.id, g.group))

    return choices

def render_detail(searchset, top_path):
    # we want to present things without repeating duplicate data, this is hard to do
    # in an html table, even with the template language, plus slow for large datasets
    searchlist = []
    lastfile = ''
    brk = "<br>"
    for s in searchset:
        if s.file_path != lastfile:
            if lastfile != '':
                searchlist.append({'file_path': lastfile.replace(top_path + "/",""), 'line_number': linenumbers, 
                                 'keyword_found': keywords})
            linenumbers = str(s.line_number)
            keywords = s.keyword_found
            lastfile = s.file_path
        else:
            linenumbers += brk + str(s.line_number)
            keywords += brk + s.keyword_found            
    
    return searchlist

