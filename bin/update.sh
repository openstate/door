#!/bin/sh
cd /opt/door
./get-cbs-areas.py >html/all.json
cp html/all.json html/all-`date '+%Y-%m-%d'`.json
