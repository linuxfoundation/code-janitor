import os
import codecs
from django.db import models, transaction

class Keyword(models.Model):
    keyword = models.CharField(max_length=80, unique=True)

    def __unicode__(self):
        return self.keyword

class Search(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    top_path = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s: %s" % (str(self.start_time), self.top_path)

    @models.permalink
    def get_absolute_url(self):
        return ("results_detail", [str(self.id)])

    @staticmethod
    @transaction.commit_on_success
    def do(top_path):
        keywords = Keyword.objects.all()
        search = Search(top_path=top_path)
        search.save()

        if os.path.isdir(top_path):
            path_iterator = os.walk(top_path)
        else:
            path_iterator = [(os.path.dirname(top_path), [], 
                              [os.path.basename(top_path)])]

        for (dir, subdirs, files) in path_iterator:
            for f in files:
                file_path = os.path.join(dir, f)
                try:
                    file_obj = open(file_path)
                    line_count = 1
                    for line in file_obj:
                        line_unicode = line.decode('utf-8', 'ignore')
                        for keyword in keywords:
                            if line_unicode.find(keyword.keyword) != -1:
                                item = SearchItem(search=search,
                                                  file_path=file_path,
                                                  keyword_found=keyword.keyword,
                                                  line_number=line_count)
                                item.save()
                        line_count = line_count + 1
                except IOError:
                    item = SearchItem(search=search, file_path=file_path,
                                      skipped=True)
                    item.save()

        return search

class SearchItem(models.Model):
    search = models.ForeignKey(Search)
    file_path = models.CharField(max_length=100)
    skipped = models.BooleanField(default=False)
    keyword_found = models.CharField(max_length=80)
    line_number = models.IntegerField(default=0)
