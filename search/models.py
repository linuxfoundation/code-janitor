import os
from django.db import models, transaction

class Keyword(models.Model):
    keyword = models.CharField(max_length=80)

class Search(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    top_path = models.CharField(max_length=100)

    @staticmethod
    @transaction.commit_on_success
    def do(top_path):
        search = Search(top_path=top_path)
        search.save()
        for (dir, subdirs, files) in os.walk(top_path):
            for f in files:
                file_path = os.path.join(dir, f)
                file_obj = open(file_path)
                line_count = 0
                for line in file_obj:
                    for keyword in keywords:
                        if line.find(keyword.keyword) >= 0:
                            item = SearchItem(search=search,
                                              file_path=file_path,
                                              keyword_found=keyword,
                                              line_number=line_count)
                            item.save()
                    line_count = line_count + 1

class SearchItem(models.Model):
    search = models.ForeignKey(Search)
    file_path = models.CharField(max_length=100)
    keyword_found = models.ForeignKey(Keyword)
    line_number = models.IntegerField()
