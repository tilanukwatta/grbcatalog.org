#!/usr/bin/env python

# source http://www.batse.msfc.nasa.gov/batse/grb/catalog/current/

#  >>python manage.py shell
#  >>execfile('insert_batse_data.py') 

# http://swift.gsfc.nasa.gov/archive/grb_table/grb_table.php?obs=Swift&year=All+Years&restrict=none&grb_time=1&grb_trigger=1&burst_advocate=1&other_obs=1&redshift=1&host=1&comments=1&references=1&bat_ra=1&bat_dec=1&bat_err_radius=1&bat_t90=1&bat_fluence=1&bat_err_fluence=1&bat_1s_peak_flux=1&bat_err_1s_peak_flux=1&bat_photon_index=1&bat_err_photon_index=1&xrt_ra=1&xrt_dec=1&xrt_err_radius=1&xrt_first_obs=1&xrt_early_flux=1&xrt_11hr_flux=1&xrt_24hr_flux=1&xrt_lc_index=1&xrt_gamma=1&xrt_nh=1&uvot_ra=1&uvot_dec=1&uvot_err_radius=1&uvot_first_obs=1&uvot_vmag=1&uvot_filters=1&view.x=20&view.y=16&view=submit

from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist
import settings
import random
setup_environ(settings)

import csv
from grbcatalog.grb.models import grb, observatory, grb_observatory_list, measurement, measurement_type, grb_type, grb_type_list, reference
from grbcatalog.datelib import julian_day
from django.contrib.auth.models import User
from datetime import date
from datetime import datetime
from django.utils.timezone import utc
import cPickle

measurement_type_ = measurement_type.objects.all()
measurement_ = measurement.objects.all()
grb_ = grb.objects.all()

"""
data_file = open('measurement_type.dat', 'wb')
cPickle.dump(measurement_type_, data_file)
data_file.close()

data_file2 = open('measurement_type.dat', 'rb')
measurement_type_ = cPickle.load(data_file2)
data_file2.close()

data_file = open('measurement.dat', 'wb')
cPickle.dump(measurement_, data_file)
data_file.close()

data_file2 = open('measurement.dat', 'rb')
measurement_ = cPickle.load(data_file2)
data_file2.close()

data_file = open('grb.dat', 'wb')
cPickle.dump(grb_, data_file)
data_file.close()

data_file2 = open('grb.dat', 'rb')
grb_ = cPickle.load(data_file2)
data_file2.close()
"""


#import ipdb; ipdb.set_trace() # debugging code
grb_data_table = []

grb_data_table_row = []
grb_data_table_row.append('GRB Name')
grb_data_table_row.append('GRB Date')
for item in measurement_type_:
    grb_data_table_row.append(item.measurement_type_name)

#grb_data_table.append(grb_data_table_row_dict.keys())
#import ipdb; ipdb.set_trace() # debugging code

for gitem in grb_:
    grb_data_table_row_dict = {}
    for item in grb_data_table_row:
        grb_data_table_row_dict.update({item:'-'})
    grb_name = gitem.grb_name
    grb_data_table_row_dict['GRB Name'] = grb_name
    for mitem in measurement_:
        if grb_name == mitem.grb_name.grb_name:
            if mitem.measurement_type.data_type == "FLOAT":
                grb_data_table_row_dict[mitem.measurement_type.measurement_type_name] = float(mitem.value)
            if mitem.measurement_type.data_type == "TEXT":
                grb_data_table_row_dict[mitem.measurement_type.measurement_type_name] = mitem.text
            if mitem.measurement_type.data_type == "DATE":
                grb_data_table_row_dict['GRB Date'] = mitem.date
                grb_data_table_row_dict[mitem.measurement_type.measurement_type_name] = mitem.date
    #grb_data_table.append(grb_data_table_row_dict.values())
    grb_data_table.append(grb_data_table_row_dict)
    #print grb_data_table
    #import ipdb; ipdb.set_trace() # debugging code

for item in grb_data_table:
    print item

data_file = open('grb_data.dat', 'wb')
cPickle.dump(grb_data_table, data_file)
data_file.close()

data_file2 = open('grb_data.dat', 'rb')
grb_data_table2 = cPickle.load(data_file2)
data_file2.close()

"""
for item in grb_data_table2:
    print item
    import ipdb; ipdb.set_trace() # debugging code
"""""

#import ipdb; ipdb.set_trace() # debugging code
#print grb_data_table2

"""
print datetime.now()
grb_data = measurement.objects.all()
#cache.set('my_key', 'hello, world!', None)
cache.set('my_key2', grb_data, None)
#query = cPickle.dumps(grb_data)
print datetime.now()
#grb_data2 = measurement.objects.all()
#print datetime.now()
#grb_data2 = cPickle.loads(query)
print cache.get('my_key2')

import pdb; pdb.set_trace() # debugging code

grb_set = []
for item in grb_data:
    grb_set.append(item.grb_name.grb_name)
print datetime.now()
"""





