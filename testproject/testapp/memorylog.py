from logging import StreamHandler

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

_log = StringIO()


# In Python 2.6, StreamHandler is an old-style class, so we derive from object
# as well so super() will work.
class MemoryHandler(StreamHandler):
    def __init__(self):
        StreamHandler.__init__(self, _log)

    @staticmethod
    def get_log():
        val = _log.getvalue()
        _log.seek(0)
        _log.truncate()
        return val
