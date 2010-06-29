from django.db import models

class Keyword(models.Model):
    keyword = models.CharField(max_length=80)

class Search(models.Model):
    start_time = models.DateTimeField()
    top_path = models.CharField(max_length=100)

class SearchItem(models.Model):
    search = models.ForeignKey(Search)
    file_path = models.CharField(max_length=100)
    keyword_found = models.ForeignKey(Keyword)
