import sys
import os
import re
import codecs
from django.db import models, transaction

class Keyword(models.Model):
    keyword = models.CharField(max_length=80, unique=True)
    reverse_search = models.BooleanField(default=False)

    def __unicode__(self):
        return self.keyword

class Group(models.Model):
    group = models.CharField(max_length=80, unique=True)

    def __unicode__(self):
        return self.group

class GroupedKeywords(models.Model):
    keyword = models.ForeignKey(Keyword)
    group = models.ForeignKey(Group)

class Search(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    top_path = models.CharField(max_length=100)
    group_list = models.CharField(max_length=100, blank=True)
    completed = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s: %s" % (str(self.start_time), self.top_path)

    @models.permalink
    def get_absolute_url(self):
        return ("results_detail", [str(self.id)])

    # This method actually does a search.  It's designed to be
    # run as a task (see util/task.py).

    @transaction.commit_on_success
    def do(self):
        sys.stdout.write("JOBDESC: Scanning files for keywords.\n")
        sys.stdout.write("MESSAGE: Loading keywords...\n")
        sys.stdout.flush()
        if self.group_list == '':
            keywords = Keyword.objects.all()
        else:
            groups = self.group_list.split(",")
            key_ids = GroupedKeywords.objects.values('keyword_id').filter(group__in=groups)
            keywords = Keyword.objects.all().filter(id__in=key_ids)

        if os.path.isdir(self.top_path):
            path_iterator = os.walk(self.top_path)
        else:
            path_iterator = [(os.path.dirname(self.top_path), [], 
                              [os.path.basename(self.top_path)])]

        sys.stdout.write("MESSAGE: Generating file list...\n")
        sys.stdout.flush()

        file_list = []
        reverse_found = {}
        for (dir, subdirs, files) in path_iterator:
            for f in files:
                file_list.append([dir, f])

        sys.stdout.write("MESSAGE: Searching files...\n")
        sys.stdout.write("COUNT: %d\n" % len(file_list))
        sys.stdout.flush()

        for (dir, f) in file_list:
            file_path = os.path.join(dir, f)
            try:
                sys.stdout.write("ITEM: " + file_path + "\n")
                sys.stdout.flush()
                file_obj = open(file_path)
                line_count = 1

                # We start assuming the word has not been found 
                for keyword in keywords:
                    reverse_found[file_path + "_" + keyword.keyword] = False

                for line in file_obj:
                    line_unicode = line.decode('utf-8', 'ignore')
                    for keyword in keywords:                        
                        if re.search(re.escape(keyword.keyword), 
                                     line_unicode, re.I):
                            if keyword.reverse_search:
                                reverse_found[file_path + "_" + keyword.keyword] = True
                            else:
                                item = SearchItem(search=self,
                                                  file_path=file_path,
                                                  keyword_found=keyword.keyword,
                                                  line_number=line_count)
                                item.save()
                    line_count = line_count + 1

                # If it's still not found after processing the whole file, log it
                for keyword in keywords:
                    if keyword.reverse_search:
                        if reverse_found[file_path + "_" + keyword.keyword] == False:
                            item = SearchItem(search=self,
                                              file_path=file_path,
                                              keyword_found=keyword.keyword,
                                              line_number=0)
                            item.save()

            except IOError, e:
                item = SearchItem(search=self, file_path=file_path,
                                  skipped=True, keyword_found=str(e))
                item.save()

        self.completed = True
        self.save()

class SearchItem(models.Model):
    search = models.ForeignKey(Search)
    file_path = models.CharField(max_length=100)
    skipped = models.BooleanField(default=False)
    keyword_found = models.CharField(max_length=80)
    # line number of zero here indicates it was a reverse search
    line_number = models.IntegerField(default=0)
