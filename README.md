metadata
========

This script will query the specified database to get a list of ultraviolet
alids.  It will then take the results and run them through varnish to pre
cache the metadata.

Dependencies:
MySQL-python python-requests python-gevent python-grequests
