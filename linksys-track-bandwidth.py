#!/usr/bin/env python2.7

from getpass import getpass
import base64
import csv
import json
import os
import requests
import sys
import time

ROUTER = '192.168.1.1'

class JNAP(object):
    def __init__(self, auth):
        self.authorization = 'Basic {}'.format(
            base64.b64encode('{}:{}'.format(*auth))
        )

    def post(self, action):
        start = time.time()
        resp = requests.post(
            'http://{}/JNAP/'.format(ROUTER),
            data='{}',
            headers={
                'X-JNAP-Authorization': self.authorization,
                'X-JNAP-Action': action,
            }
        )
        end = time.time()

        return start, end, resp

class TeeCSV(object):
    def __init__(self, fn):
        self.fp = open(fn, 'a')
        self.stdout = sys.stdout

        self.csv_fp = csv.writer(self.fp)
        self.csv_stdout = csv.writer(self.stdout)

    def writerow(self, row):
        self.csv_fp.writerow(row)
        self.csv_stdout.writerow(row)

def main():
    auth = ['admin']
    auth.append(getpass())

    jnap = JNAP(auth)
    tee = TeeCSV('bandwidth.log')
    format = lambda r: [r[0], r[1], json.dumps(r[2].json())]
    try:
        while True:
            row = []
            row.extend(format(jnap.post('http://linksys.com/jnap/networktraffic/BeginStatisticsTracking')))
            time.sleep(1)
            row.extend(format(jnap.post('http://linksys.com/jnap/networktraffic/GetStatisticsByDevice')))
            tee.writerow(row)
            time.sleep(1)
    except KeyboardInterrupt:
        sys.stderr.write('exiting...\n')

    return 0

if __name__ == '__main__':
    sys.exit(main())
