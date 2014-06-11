from cStringIO import StringIO
from logging import StreamHandler

_log = StringIO()


class MemoryHandler(StreamHandler):
    def __init__(self):
        super(MemoryHandler, self).__init__(stream=_log)

    @staticmethod
    def get_log():
        val = _log.getvalue()
        _log.reset()
        _log.truncate()
        return val
