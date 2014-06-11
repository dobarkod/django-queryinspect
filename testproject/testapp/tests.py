from django.test import TestCase

from .models import Author, Book, Publisher
from .memorylog import MemoryHandler


class TestFoo(TestCase):

    def test_query_inspect(self):
        self.author = Author.objects.create(name='Author')
        self.publisher = Publisher.objects.create(name='Publisher')
        for i in range(10):
            Book.objects.create(
                title='Book %d' % i,
                author=self.author,
                publisher=self.publisher)

        with self.settings(DEBUG=True):
            self.client.get('/authors/')

        log = MemoryHandler.get_log()
        lines = log.split('\n')

        repeated_query = '[SQL] repeated query (10x):'
        has_repeated_query = False
        stats = '[SQL] 12 queries (9 duplicates),'
        has_stats = False

        for line in lines:
            if line.startswith(repeated_query):
                has_repeated_query = True
            if line.startswith(stats):
                has_stats = True

        self.assertTrue(has_repeated_query,
            msg="Log doesn't have correct repeated query: '" + repeated_query +
                '\'\n"""\n' + log + '"""')
        self.assertTrue(has_stats,
            msg="Log doesn't have correct stats: '" + stats +
                '\'\n"""\n' + log + '"""')