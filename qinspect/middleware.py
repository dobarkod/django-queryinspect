import logging
import collections
import re
import time
import traceback
import math

from django.conf import settings
from django.db import connection
from django.db.backends.util import CursorDebugWrapper

log = logging.getLogger('qinspect')

cfg = dict(
    enabled=(settings.DEBUG and
        getattr(settings, 'QUERY_INSPECT_ENABLED', False)),
    log_stats=getattr(settings, 'QUERY_INSPECT_LOG_STATS', True),
    header_stats=getattr(settings, 'QUERY_INSPECT_HEADER_STATS', True),
    log_queries=getattr(settings, 'QUERY_INSPECT_LOG_QUERIES', False),
    log_tbs=getattr(settings, 'QUERY_INSPECT_LOG_TRACEBACKS', False),
    roots=getattr(settings, 'QUERY_INSPECT_TRACEBACK_ROOTS', None),
    stddev_limit=getattr(settings, 'QUERY_INSPECT_STANDARD_DEVIATION_LIMIT', None),
    absolute_limit=getattr(settings, 'QUERY_INSPECT_ABSOLUTE_LIMIT', None),
)

__all__ = ['QueryInspectMiddleware']


class QueryInspectMiddleware(object):

    class QueryInfo(object):
        __slots__ = ('sql', 'time', 'tb')

    sql_id_pattern = re.compile(r'=\s*\d+')

    @classmethod
    def patch_cursor(cls):
        real_exec = CursorDebugWrapper.execute
        real_exec_many = CursorDebugWrapper.executemany

        def should_include(path):
            if path == __file__ or path + 'c' == __file__:
                return False
            if not cfg['roots']:
                return True
            else:
                for root in cfg['roots']:
                    if path.startswith(root):
                        return True
                return False

        def tb_wrap(fn):
            def wrapper(self, *args, **kwargs):
                try:
                    return fn(self, *args, **kwargs)
                finally:
                    if hasattr(self.db, 'queries'):
                        tb = traceback.extract_stack()
                        tb = [f for f in tb if should_include(f[0])]
                        self.db.queries[-1]['tb'] = tb

            return wrapper

        CursorDebugWrapper.execute = tb_wrap(real_exec)
        CursorDebugWrapper.executemany = tb_wrap(real_exec_many)

    @classmethod
    def get_query_infos(cls, queries):
        retval = []
        for q in queries:
            qi = cls.QueryInfo()
            qi.sql = cls.sql_id_pattern.sub('= ?', q['sql'])
            qi.time = float(q['time'])
            qi.tb = q.get('tb')
            retval.append(qi)
        return retval

    @staticmethod
    def count_duplicates(infos):
        buf = collections.defaultdict(lambda: 0)
        for qi in infos:
            buf[qi.sql] = buf[qi.sql] + 1
        return sorted(buf.items(), key=lambda el: el[1], reverse=True)

    @staticmethod
    def group_queries(infos):
        buf = collections.defaultdict(lambda: [])
        for qi in infos:
            buf[qi.sql].append(qi)
        return buf

    def process_request(self, request):
        if not cfg['enabled']:
            return

        self.request_start = time.time()
        self.conn_queries_len = len(connection.queries)

    def process_response(self, request, response):
        if not hasattr(self, 'request_start'):
            return response

        request_time = time.time() - self.request_start
        qis = self.get_query_infos(connection.queries[self.conn_queries_len:])
        qis_len = len(qis)
        sql_time = sum(qi.time for qi in qis)

        duplicates = [(qi, num) for qi, num in self.count_duplicates(qis)
            if num > 1]
        duplicates.reverse()
        num_duplicates = 0
        if len(duplicates) > 0:
            num_duplicates = (sum(num for qi, num in duplicates) -
                len(duplicates))

        dup_groups = self.group_queries(qis)

        if cfg['log_queries']:
            for sql, num in duplicates:
                log.warning('[SQL] repeated query (%dx): %s' % (num, sql))
                if cfg['log_tbs'] and dup_groups[sql]:
                    log.warning('Traceback:\n' +
                        ''.join(traceback.format_list(dup_groups[sql][0].tb)))

        if cfg['stddev_limit'] is not None and qis_len > 0:
            mean = sql_time / qis_len
            stddev_sum = sum([math.sqrt((qi.time-mean)**2) for qi in qis])
            stddev = math.sqrt((1.0/(qis_len-1))*(stddev_sum/qis_len))

            query_limit = mean + (stddev * cfg['stddev_limit'])

            for qi in qis:
                if qi.time > query_limit:
                    log.warning('[SQL] query execution of %d ms over limit of %d ms (%d dev above mean): %s' % (
                        qi.time * 1000,
                        query_limit * 1000,
                        cfg['stddev_limit'],
                        qi.sql))
                    
        if cfg['absolute_limit'] is not None and qis_len > 0:
            query_limit = cfg['absolute_limit'] / 1000.0

            for qi in qis:
                if qi.time > query_limit:
                    log.warning('[SQL] query execution of %d ms over absolute limit of %d ms: %s' % (
                        qi.time * 1000,
                        query_limit * 1000,
                        qi.sql))

        if cfg['log_stats']:
            log.info('[SQL] %d queries (%d duplicates), %d ms SQL time, '
                '%d ms total request time' % (
                    qis_len,
                    num_duplicates,
                    sql_time * 1000,
                    request_time * 1000))

        if cfg['header_stats']:
            response['X-QueryInspect-Num-SQL-Queries'] = str(len(qis))
            response['X-QueryInspect-Total-SQL-Time'] = '%d ms' % (
                sql_time * 1000)
            response['X-QueryInspect-Total-Request-Time'] = '%d ms' % (
                request_time * 1000)
            response['X-QueryInspect-Duplicate-SQL-Queries'] = str(
                num_duplicates)

        return response


if cfg['enabled'] and cfg['log_tbs']:
    QueryInspectMiddleware.patch_cursor()
