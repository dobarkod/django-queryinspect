# Django Query Inspector

[![Build Status](https://travis-ci.org/dobarkod/django-queryinspect.svg?branch=master)](https://travis-ci.org/dobarkod/django-queryinspect?branch=master)

Query Inspector is a Django application providing middleware for inspecting
and reporting SQL queries executed for each web request.

Works with Django (1.4, 1.5, 1.6, 1.7) and Python (2.6, 2.7, 3.3, 3.4).

Example log output:

    [SQL] 17 queries (4 duplicates), 34 ms SQL time, 243 ms total request time

The statistics can also be added to reponse headers, for easier debugging
without looking into the server logs:

    X-QueryInspect-Num-SQL-Queries: 17
    X-QueryInspect-Duplicate-SQL-Queries: 4
    X-QueryInspect-Total-SQL-Time: 34 ms
    X-QueryInspect-Total-Request-Time: 243 ms

The duplicate queries can also be shown in the log:

    [SQL] repeated query (6x): SELECT "customer_role"."id",
        "customer_role"."contact_id", "customer_role"."name"
        FROM "customer_role" WHERE "customer_role"."contact_id" = ?

The duplicate queries are detected by ignoring any integer values in the SQL
statement. The reasoning is that most of the duplicate queries in Django are
due to results not being cached or pre-fetched properly, so Django needs to
look up related fields afterwards. This lookup is done by the object ID, which
is in most cases an integer.

The heuristic is not 100% precise so it may have some false positives or
negatives, but is a very good starting point for most Django projects.

For each duplicate query, the Python traceback can also be shown, which may
help with identifying why the query has been executed:

    File "/vagrant/api/views.py", line 178, in get
        return self.serialize(self.object_qs)
    File "/vagrant/customer/views.py", line 131, in serialize
        return serialize(objs, include=includes)
    File "/vagrant/customer/serializers.py", line 258, in serialize_contact
        lambda obj: [r.name for r in obj.roles.all()]),
    File "/vagrant/customer/serializers.py", line 258, in <lambda>
        lambda obj: [r.name for r in obj.roles.all()]),

## Quickstart

Install from the Python Package Index:

    pip install django-queryinspect

Add the middleware to your Django settings:

    MIDDLEWARE_CLASSES += (
        'qinspect.middleware.QueryInspectMiddleware',
    )

Enable Django's `DEBUG` setting (the SQL query logging doesn't work without
it):

    DEBUG = True

And set one or more Query Inspector settings flags depending on the desired
behaviour:

    # Whether the Query Inspector should do anything (default: False)
    QUERY_INSPECT_ENABLED = True
    # Whether to log the stats via Django logging (default: True)
    QUERY_INSPECT_LOG_STATS = True
    # Whether to add stats headers (default: True)
    QUERY_INSPECT_HEADER_STATS = True
    # Whether to log duplicate queries (default: False)
    QUERY_INSPECT_LOG_QUERIES = True
    # Whether to include tracebacks in the logs (default: False)
    QUERY_INSPECT_LOG_TRACEBACKS = True
    # Project root (one or several colon-separated directories, default empty)
    QUERY_INSPECT_TRACEBACK_ROOTS = '/path/to/my/django/project/'

## Traceback roots

Complete tracebacks of an entire request are usually huge, but only a few
entries in the traceback are of the interest (usually only the few that
represent the code you're working on). To include only these entries of interest
in the shown tracebacks, you can set `QUERY_INSPECT_TRACEBACK_ROOTS` to the
root directory of your project.

Since Django apps need not be under the same directory, the setting also
accepts colon-separated list of directories - traceback entry referencing any
file under any of these directories will be included.

## License

Copyright (C) 2014. Good Code

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
