#!/bin/sh
#
set -e
#
DB="meddra"
#
#
psql -c "DROP DATABASE $DB"
#

