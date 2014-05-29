#!/usr/bin/env python

# This script will query the specified database to get a list of ultraviolet
# alids.  It will then take the results and run them through varnish to pre
# cache the metadata.

# Dependencies:
# yum install MySQL-python python-requests python-gevent python-grequests

import MySQLdb as mdb
import sys
import grequests
import requests


MYSQL_HOST = ""
MYSQL_USER = ""
MYSQL_PASS = ""
MYSQL_DB = ""
MYSQL_QUERY = "SELECT x FROM y WHERE metadata is not NULL"
API_KEY_HEADER = {'Authorization': ''}
VARNISH_URLS = [""]


def getAlids():
    try:
        con = mdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)

        cur = con.cursor()
        cur.execute(MYSQL_QUERY)

        rows = cur.fetchall()

        return rows

    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

    finally:
        if con:
            con.close()


def callCache(rows):
    goodCount = 0
    badCount = 0

    try:
        for row in rows:
            varnishGet = [grequests.get(u.format(row[0]), headers=API_KEY_HEADER, data=None, timeout=10) for u in VARNISH_URLS]
            responses = grequests.map(varnishGet, size=5)

            for response in responses:
                if response.status_code != 200:
                    print "Error %s on URL %s" % (response.status_code, response.url)
                    badCount = badCount + 1
                else:
                    goodCount = goodCount + 1
        print "Sucessful cache requests: %s" % (goodCount)
        print "Failed cache requests: %s" % (badCount)

    except requests.HTTPError, e:
        print 'HTTP ERROR %s occured' % e.code
        print e


def main():
    print "Getting alids from db.."
    rows = getAlids()
    print "Populating varnish cache.."
    callCache(rows)

if __name__ == '__main__':
    main()

