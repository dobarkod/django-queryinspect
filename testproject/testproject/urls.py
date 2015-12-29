from django.conf.urls import url, include
from django import VERSION

from testapp.views import get_authors_with_books, book

if VERSION >= (1, 9):
    def patterns(prefix, *args):
        return args
else:
    from django.conf.urls import patterns

urlpatterns = patterns('testapp.views',
    url(r'^authors/$', get_authors_with_books, name='authors'),
    url(r'^book/$', book, name='book'),
)
