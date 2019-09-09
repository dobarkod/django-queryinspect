from django.test import TestCase

from .models import Author, Book, Publisher
from .memorylog import MemoryHandler


class TestQueryInspect(TestCase):

    def test_single_query_view(self):
        self.author = Author.objects.create(name='Author')
        self.publisher = Publisher.objects.create(name='Publisher')
        for i in range(10):
            Book.objects.create(
                title='Book %d' % i,
                author=self.author,
                publisher=self.publisher)

        with self.settings(DEBUG=True):
            response = self.client.get('/book/')

        log = MemoryHandler.get_log()
        lines = log.split('\n')

        stats = '[SQL] 1 queries (0 duplicates),'
        has_stats = False
        boring_traceback_entry = 'django/db/models/query.py'
        has_boring_traceback_entry = False
        over_absolute_limit = 'over absolute limit of -1 ms'
        has_over_absolute_limit = False
        for line in lines:
            if line.startswith(stats):
                has_stats = True
            if boring_traceback_entry in line:
                has_boring_traceback_entry = True
            if over_absolute_limit in line:
                has_over_absolute_limit = True

        self.assertTrue(
            has_stats,
            msg="Log doesn't have correct stats: '" + stats +
                '\'\n"""\n' + log + '"""')
        self.assertFalse(
            has_boring_traceback_entry,
            msg='Log contains extraneous traceback entries\n"""\n' +
                log + '"""')
        self.assertTrue(
            has_over_absolute_limit,
            msg='Log doesn\'t have over absolute limit warning\n"""\n' +
                log + '"""')

        self.assertEqual(response['X-QueryInspect-Num-SQL-Queries'], '1')
        self.assertTrue('X-QueryInspect-Total-Request-Time' in response)
        self.assertEqual(response['X-QueryInspect-Duplicate-SQL-Queries'], '0')

    def test_query_inspect(self):
        self.author = Author.objects.create(name='Author')
        self.publisher = Publisher.objects.create(name='Publisher')
        for i in range(10):
            Book.objects.create(
                title='Book %d' % i,
                author=self.author,
                publisher=self.publisher)

        with self.settings(DEBUG=True):
            response = self.client.get('/authors/')

        log = MemoryHandler.get_log()
        lines = log.split('\n')

        repeated_query = '[SQL] repeated query (10x):'
        has_repeated_query = False
        stats = '[SQL] 12 queries (9 duplicates),'
        has_stats = False
        boring_traceback_entry = 'django/db/models/query.py'
        has_boring_traceback_entry = False
        over_absolute_limit = 'over absolute limit of -1 ms'
        has_over_absolute_limit = False

        for line in lines:
            if line.startswith(repeated_query):
                has_repeated_query = True
            if line.startswith(stats):
                has_stats = True
            if boring_traceback_entry in line:
                has_boring_traceback_entry = True
            if over_absolute_limit in line:
                has_over_absolute_limit = True

        self.assertTrue(has_repeated_query,
            msg="Log doesn't have correct repeated query: '" + repeated_query +
                '\'\n"""\n' + log + '"""')
        self.assertTrue(has_stats,
            msg="Log doesn't have correct stats: '" + stats +
                '\'\n"""\n' + log + '"""')
        self.assertFalse(has_boring_traceback_entry,
            msg='Log contains extraneous traceback entries\n"""\n' +
                log + '"""')
        self.assertTrue(has_over_absolute_limit,
            msg='Log doesn\'t have over absolute limit warning\n"""\n' +
                log + '"""')

        self.assertEqual(response['X-QueryInspect-Num-SQL-Queries'], '12')
        self.assertTrue('X-QueryInspect-Total-Request-Time' in response)
        self.assertEqual(response['X-QueryInspect-Duplicate-SQL-Queries'], '9')

    def test_sql_truncate(self):
        self.author = Author.objects.create(name='Author')

        with self.settings(DEBUG=True):
            response = self.client.get('/authors/')

        log = MemoryHandler.get_log()
        lines = log.split('\n')

        has_truncated = False
        for line in lines:
            if 'SELECT "testapp_book"' in line and ' ... ' in line:
                has_truncated = True
                break

        self.assertTrue(has_truncated, msg='Log didn\'t truncate SQL output')
