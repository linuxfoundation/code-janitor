from django.test import TestCase

from janitor.search import models

class TestSearch(TestCase):
    fixtures = ["test_keyword_data.xml"]

    def testSearch(self):
        s = models.Search(top_path="./testdata/search_test.txt")
        s.save()
        s.do()

        self.assertTrue(s.searchitem_set.count() > 0)
