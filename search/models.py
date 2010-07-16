import sys
import os
import re
import codecs
from django.db import models, transaction

class Keyword(models.Model):
    keyword = models.CharField(max_length=80, unique=True)

    def __unicode__(self):
        return self.keyword

class Search(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    top_path = models.CharField(max_length=100)
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
        keywords = Keyword.objects.all()

        if os.path.isdir(self.top_path):
            path_iterator = os.walk(self.top_path)
        else:
            path_iterator = [(os.path.dirname(self.top_path), [], 
                              [os.path.basename(self.top_path)])]

        for (dir, subdirs, files) in path_iterator:
            for f in files:
                file_path = os.path.join(dir, f)
                try:
                    sys.stdout.write("ITEM: " + file_path + "\n")
                    sys.stdout.flush()
                    file_obj = open(file_path)
                    line_count = 1
                    for line in file_obj:
                        line_unicode = line.decode('utf-8', 'ignore')
                        for keyword in keywords:
                            if re.search(re.escape(keyword.keyword), 
                                         line_unicode, re.I):
                                item = SearchItem(search=self,
                                                  file_path=file_path,
                                                  keyword_found=keyword.keyword,
                                                  line_number=line_count)
                                item.save()
                        line_count = line_count + 1
                except IOError:
                    item = SearchItem(search=self, file_path=file_path,
                                      skipped=True)
                    item.save()

        self.completed = True
        self.save()

class SearchItem(models.Model):
    search = models.ForeignKey(Search)
    file_path = models.CharField(max_length=100)
    skipped = models.BooleanField(default=False)
    keyword_found = models.CharField(max_length=80)
    line_number = models.IntegerField(default=0)
