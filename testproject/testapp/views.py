import json
from django.http import HttpResponse
from .models import Author, Book


class JsonResponse(HttpResponse):
    def __init__(self, data):
        super(JsonResponse, self).__init__(json.dumps(data),
            content_type='application/json; charset=utf-8')


def get_authors_with_books(request):
    authors = []
    for a in Author.objects.all():
        author = {'name': a.name, 'books': []}
        for b in a.books.all():
            author['books'].append({
                'title': b.title,
                'publisher': b.publisher.name
            })
        authors.append(author)

    return JsonResponse(authors)


def book(request):
    book = Book.objects.all()[0]
    return JsonResponse({'title': book.title})
