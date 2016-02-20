#!/bin/sh

#tar xvfz grbcatalog_database.sql.tar.gz
mysql -u hawc -p grbcatalog < grbcatalog_database.sql

