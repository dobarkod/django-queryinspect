from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=200)


class Publisher(models.Model):
    name = models.CharField(max_length=200)


class Book(models.Model):
    author = models.ForeignKey(Author, related_name='books')
    publisher = models.ForeignKey(Publisher, related_name='books')
    title = models.CharField(max_length=200)
