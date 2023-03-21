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

def _normalize_date_from_descrpition(description, year):
    if description is not None:
        orig = description.split(' ')[-1]
        if re.match('^\d{4}', orig):
            orig = "%s-01-01" % (orig,)
        m = re.match('(\d{2})-(\d{2})-(\d{4})', orig)
        if m is not None:
            orig = "%s-%s-%s" % (m.group(3), m.group(2), m.group(1),)
        return orig
    else:
        return "%s-01-01" % (year,)

def _normalize_cbs_code(key):
    if key.startswith('GM'):
        return key.strip()
    else:
        return 'GM%s' % (key.strip(),)

def get_areas_for_table(table, year):
    resp = requests.get('https://opendata.cbs.nl/ODataFeed/OData/%s/RegioS?$format=json' % (table,))
    if resp.status_code < 200 or resp.status_code >= 300:
        return
    data = resp.json()
    result = [{
        'id': _normalize_cbs_code(a['Key']),
        'name': a['Title'],
        'created': _normalize_date_from_descrpition(a['Description'], year),
        'dissolved': "%s-12-31" % (year,)
    } for a in data['value']]
    return result

def get_normalized_areas_for_tables(tables):
    result = {}
    print(tables)
    for t in tables:
        year = int(t['title'].split(' ')[-1])
        print(year, t['title'])
        areas = get_areas_for_table(t['id'], year)
        if areas is not None:
            for a in areas:
                current_id = a['id']
                if current_id not in result:
                    result[current_id] = a
                if a['created'] and (a['created'] < result[current_id]['created']):
                    result[current_id]['created'] = a['created']
                if a['dissolved'] > result[current_id]['dissolved']:
                    result[current_id]['dissolved'] = a['dissolved']
        sleep(1)
    return result

def main(argv):
    tables = get_area_tables()
    municipalities = get_normalized_areas_for_tables(tables)
    pprint(municipalities)
    #print("--> check:")
    #pprint(municipalities['GMG365'])
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
