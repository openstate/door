#!/usr/bin/env python

import os
import sys
import re
from time import sleep
from pprint import pprint

import requests

def get_area_tables():
    catalog = requests.get('https://opendata.cbs.nl/ODataCatalog/Tables/?$format=json').json()
    result = []
    for c in catalog['value']:
        if c['Title'].lower().startswith('gebieden in nederland'):
            result.append({'id': c['Identifier'], 'title': c['Title']})
    return result

def _normalize_date_from_descrpition(description):
    if description is not None:
        return description.split(' ')[-1]

def get_areas_for_table(table, year):
    resp = requests.get('https://opendata.cbs.nl/ODataFeed/OData/%s/RegioS?$format=json' % (table,))
    if resp.status_code < 200 or resp.status_code >= 300:
        return
    data = resp.json()
    result = [{
        'id': 'GM%s' % (a['Key'].strip(),),
        'name': a['Title'],
        'created': _normalize_date_from_descrpition(a['Description']),
        'year': year
    } for a in data['value']]
    return result

def main(argv):
    tables = get_area_tables()
    print(tables)
    for t in tables:
        year = int(t['title'].split(' ')[-1])
        print(year, t['title'])
        areas = get_areas_for_table(t['id'], year)
        if areas is not None:
            pprint(areas)
        sleep(1)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
