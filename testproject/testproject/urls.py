from django.conf.urls import patterns, url

urlpatterns = patterns('testapp.views',
    url(r'^authors/$', 'get_authors_with_books', name='authors'),
)
