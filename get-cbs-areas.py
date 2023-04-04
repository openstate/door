#!/usr/bin/env python

import os
import sys
import re
from time import sleep
from pprint import pprint
from datetime import datetime
import json

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
    if key.startswith('GM') or key.startswith('PV'):
        return key.strip()
    else:
        return 'GM%s' % (key.strip(),)

def get_areas_for_table(table, year, table_type):
    resp = requests.get('https://opendata.cbs.nl/ODataFeed/OData/%s/RegioS?$format=json' % (table,))
    if resp.status_code < 200 or resp.status_code >= 300:
        return
    data = resp.json()
    if table_type == 'Gemeente':
        title_prefix = ''
    else:
        title_prefix = '%s ' % (table_type,)
    result = [{
        'id': _normalize_cbs_code(a['Key']),
        'name': '%s%s' % (title_prefix, a['Title'].replace(' (PV)', ''),),
        'type': table_type,
        'created': _normalize_date_from_descrpition(a['Description'], year),
        'dissolved': "%s-12-31" % (year,)
    } for a in data['value']]
    return result

def get_normalized_areas_for_tables(tables, table_type):
    result = {}
    #print(tables)
    for t in tables:
        year = int(t['title'].split(' ')[-1])
        #print(year, t['title'])
        areas = get_areas_for_table(t['id'], year, table_type)
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

def get_provinces(current_year):
    # This is all a bit hacky because provinces don't change much in terms of existence
    province_areas = get_areas_for_table('70739ned', current_year, 'Provincie')  # hardcoded!
    for p in province_areas:
        # Flevoland is the only province with a creation date after 1815
        if p['id'] == 'PV24':
            p['created'] = '1986-01-01'
        else:
            p['created'] = '1815-01-01'
    provinces = {a['id']: a for a in province_areas if a['id'].startswith('PV')}
    return provinces

def main(argv):
    current_date = datetime.now()
    current_year = datetime.now().year
    provinces = get_provinces(current_year)
    tables = get_area_tables()
    municipalities = get_normalized_areas_for_tables(tables, 'Gemeente')
    for k in [provinces, municipalities]:
        for i in k:
            if k[i]['dissolved'] > current_date.isoformat()[0:10]:
                k[i]['dissolved'] = None
    print(json.dumps(list(provinces.values()) + list(municipalities.values())))
    #print("--> check:")
    #pprint(municipalities['GMG365'])
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
