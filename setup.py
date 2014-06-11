#!/usr/bin/env python

from setuptools import setup, find_packages, Command
import os
import sys


class BaseCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class TestCommand(BaseCommand):

    description = "run self-tests"

    def run(self):
        os.chdir('testproject')
        ret = os.system('python manage.py test testapp')
        if ret != 0:
            sys.exit(-1)

setup(
    name='django-queryinspect',
    version='0.0.1',
    author='Senko Rasic',
    author_email='senko.rasic@goodcode.io',
    description='Django Query Inspector',
    license='MIT',
    url='https://github.com/dobarkod/django-queryinspect',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    install_requires=['Django>=1.4'],
    cmdclass={
        'test': TestCommand,
    }
)
