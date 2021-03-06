"""
Author : Tilan Ukwatta (tilan.ukwatta@gmail.com)
"""
import django
#from django.template.loader import get_template
#from django.template import Context
from django.http import HttpResponse
#from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from grbcatalog.grb.models import grb, measurement, measurement_type, grb_type, grb_type_list, observatory, grb_observatory_list, reference, help
#from hawcmon.datelib import julian_day
from datetime import date
import math
from django.shortcuts import render_to_response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_pdf import FigureCanvasPdf as PdfFigureCanvas
from matplotlib.figure import Figure
from django.utils.timezone import datetime
from datetime import timedelta
from django.utils.timezone import utc
import csv
import cPickle
import grbcatalog.data_statistics as ds
import pandas
import grbcatalog.machinez as machinez
import grbcatalog.gpose_analysis as gpose
import grbcatalog.gpose_sky_model as gpose_sky
import numpy as np
import grbcatalog.secrets as secrets

login_url = '/admin/'

if secrets.site == 'local':
    grb_data_file = '/home/tilan/Desktop/Dropbox/django/grbcatalog/grbcatalog/grb_data.dat'
    machine_z_data_file = '/home/tilan/Desktop/Dropbox/django/grbcatalog/grbcatalog/machine-z/grb_data_sample_num_284_f25.csv'
    feature_key_map = '/home/tilan/Desktop/Dropbox/django/grbcatalog/grbcatalog/machine-z/feature_key_map.dat'
    gpose_sim_parameters = '/home/tilan/Desktop/Dropbox/django/grbcatalog/grbcatalog/gpose/gpose_sim_parameters.dat'
elif secrets.site == 'dev':
    grb_data_file = '/home/tilan/work/grbcatalog.org/grbcatalog/grb_data.dat'
    machine_z_data_file = '/home/tilan/work/grbcatalog.org/grbcatalog/machine-z/grb_data_sample_num_284_f25.csv'
    feature_key_map = '/home/tilan/work/grbcatalog.org/grbcatalog/machine-z/feature_key_map.dat'
    gpose_sim_parameters = '/home/tilan/work/grbcatalog.org/grbcatalog/gpose/gpose_sim_parameters.dat'
elif secrets.site == 'msu':
    grb_data_file = '/web_app/grbcatalog/grbcatalog/grb_data.dat'
    machine_z_data_file = '/web_app/grbcatalog/grbcatalog/machine-z/grb_data_sample_num_284_f25.csv'
    feature_key_map = '/web_app/grbcatalog/grbcatalog/machine-z/feature_key_map.dat'
    gpose_sim_parameters = '/web_app/grbcatalog/grbcatalog/gpose/gpose_sim_parameters.dat'
else:
    grb_data_file = '/home/tilanukwatta/grbcatalog.org/grbcatalog/grb_data.dat'
    machine_z_data_file = '/home/tilanukwatta/grbcatalog.org/grbcatalog/machine-z/grb_data_sample_num_284_f25.csv'
    feature_key_map = '/home/tilanukwatta/grbcatalog.org/grbcatalog/machine-z/feature_key_map.dat'
    gpose_sim_parameters = '/home/tilanukwatta/grbcatalog.org/grbcatalog/gpose/gpose_sim_parameters.dat'

def get_set_intersection(set1, set2):
    set3 = []
    for item in set1:
        if item in set2:
            set3.append(item)
    return set3

def get_grb_sample1(request):
    parameters = []
    year = timedelta(days=365)
    week = timedelta(days=7)
    day = timedelta(days=1)
    cur_time = datetime.utcnow()
    #cur_time = cur_time.replace(year=cur_time.year, month=cur_time.month, day=cur_time.day, hour=cur_time.hour, minute=cur_time.minute, second=cur_time.second, microsecond=0, tzinfo=utc)
    #default_date = cur_time - week
    cur_time = cur_time.replace(year=cur_time.year, month=cur_time.month, day=cur_time.day, hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)
    default_date = cur_time - (week * 12)

    num_cuts = request.GET.get('num_cuts', 0)
    parameters.append(num_cuts)
    no_date_cut = request.GET.get('no_date_cut', 'False')
    parameters.append(no_date_cut)

    x_year_min = int(request.GET.get('x_year_min', default_date.year))
    parameters.append(x_year_min)
    x_month_min = int(request.GET.get('x_month_min', default_date.month))
    parameters.append(x_month_min)
    x_day_min = int(request.GET.get('x_day_min', default_date.day))
    parameters.append(x_day_min)
    x_hour_min = int(request.GET.get('x_hour_min', default_date.hour))
    parameters.append(x_hour_min)
    x_min_min = int(request.GET.get('x_min_min', default_date.minute))
    parameters.append(x_min_min)
    x_sec_min = int(request.GET.get('x_sec_min', default_date.second))
    parameters.append(x_sec_min)

    x_year_max = int(request.GET.get('x_year_max', cur_time.year))
    parameters.append(x_year_max)
    x_month_max = int(request.GET.get('x_month_max', cur_time.month))
    parameters.append(x_month_max)
    x_day_max = int(request.GET.get('x_day_max', cur_time.day))
    parameters.append(x_day_max)
    x_hour_max = int(request.GET.get('x_hour_max', cur_time.hour))
    parameters.append(x_hour_max)
    x_min_max = int(request.GET.get('x_min_max', cur_time.minute))
    parameters.append(x_min_max)
    x_sec_max = int(request.GET.get('x_sec_max', cur_time.second))
    parameters.append(x_sec_max)

    x_min = datetime.utcnow()
    x_max = datetime.utcnow()

    if no_date_cut == 'True':
        x_year_min = 1900
        x_year_max = 2100

    x_min = x_min.replace(year=x_year_min, month=x_month_min, day=x_day_min, hour=x_hour_min, minute=x_min_min, second=x_sec_min, microsecond=0, tzinfo=utc)
    x_max = x_max.replace(year=x_year_max, month=x_month_max, day=x_day_max, hour=x_hour_max, minute=x_min_max, second=x_sec_max, microsecond=0, tzinfo=utc)

    grb_set = []
    grb_table = measurement.objects.filter(date__range = (x_min, x_max)).order_by('grb_name')

    for item in grb_table:
        grb_set.append(item.grb_name.grb_name)

    cut_array = []
    for i in range(0, int(num_cuts), 1):
        cut_row = []
        cut_row.append(str('cut_')+str(i)+'_min')
        cut_row.append(str('cut_')+str(i))
        cut_row.append(str('cut_')+str(i)+'_max')
        #cut_row.append('') # cut min value (index - 3)
        #cut_row.append('') # cut max value (index - 4)
        #cut_row.append('') # cut variable  (index - 5)
        commnd_str = "cut_row.append(request.GET.get('cut_" + str(i) + "_min' , '0'))" # cut min value (index - 3)
        exec commnd_str
        commnd_str = "cut_row.append(request.GET.get('cut_" + str(i) + "_max' , '2'))" # cut max value (index - 4)
        exec commnd_str
        commnd_str = "cut_row.append(request.GET.get('cut_" + str(i) + "' , r'BAT T90'))" # cut variable (index - 5)
        exec commnd_str
        cut_array.append(cut_row)
    parameters.append(cut_array)

    cut_set = []
    if num_cuts > 0:
        for cut_item in cut_array:
            grb_sub_set = []
            cut_value_min = float(cut_item[3])
            cut_value_max = float(cut_item[4])
            #import pdb; pdb.set_trace() # debugging code
            cut_measurement_type = measurement_type.objects.get(measurement_type_name=cut_item[5])
            cut_measurement = measurement.objects.filter(measurement_type=cut_measurement_type, value__lte=cut_value_max, value__gte=cut_value_min)
            cut_set.append(cut_measurement_type.measurement_type_id)
            for item in cut_measurement:
                grb_sub_set.append(item.grb_name.grb_name)
            grb_set = get_set_intersection(grb_set, grb_sub_set)
            #import pdb; pdb.set_trace() # debugging code

    return grb_set, parameters

def get_grb_sample2(request):
    parameters = []
    year = timedelta(days=365)
    week = timedelta(days=7)
    day = timedelta(days=1)
    cur_time = datetime.utcnow()
    #cur_time = cur_time.replace(year=cur_time.year, month=cur_time.month, day=cur_time.day, hour=cur_time.hour, minute=cur_time.minute, second=cur_time.second, microsecond=0, tzinfo=utc)
    #default_date = cur_time - week
    cur_time = cur_time.replace(year=cur_time.year, month=cur_time.month, day=cur_time.day, hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)
    default_date = cur_time - (week * 12)

    num_cuts = request.GET.get('num_cuts', 0)
    parameters.append(num_cuts)
    no_date_cut = request.GET.get('no_date_cut', 'False')
    parameters.append(no_date_cut)

    x_year_min = int(request.GET.get('x_year_min', default_date.year))
    parameters.append(x_year_min)
    x_month_min = int(request.GET.get('x_month_min', default_date.month))
    parameters.append(x_month_min)
    x_day_min = int(request.GET.get('x_day_min', default_date.day))
    parameters.append(x_day_min)
    x_hour_min = int(request.GET.get('x_hour_min', default_date.hour))
    parameters.append(x_hour_min)
    x_min_min = int(request.GET.get('x_min_min', default_date.minute))
    parameters.append(x_min_min)
    x_sec_min = int(request.GET.get('x_sec_min', default_date.second))
    parameters.append(x_sec_min)

    x_year_max = int(request.GET.get('x_year_max', cur_time.year))
    parameters.append(x_year_max)
    x_month_max = int(request.GET.get('x_month_max', cur_time.month))
    parameters.append(x_month_max)
    x_day_max = int(request.GET.get('x_day_max', cur_time.day))
    parameters.append(x_day_max)
    x_hour_max = int(request.GET.get('x_hour_max', cur_time.hour))
    parameters.append(x_hour_max)
    x_min_max = int(request.GET.get('x_min_max', cur_time.minute))
    parameters.append(x_min_max)
    x_sec_max = int(request.GET.get('x_sec_max', cur_time.second))
    parameters.append(x_sec_max)

    x_min = datetime.utcnow()
    x_max = datetime.utcnow()

    if no_date_cut == 'True':
        x_year_min = 1900
        x_year_max = 2100

    x_min = x_min.replace(year=x_year_min, month=x_month_min, day=x_day_min, hour=x_hour_min, minute=x_min_min, second=x_sec_min, microsecond=0, tzinfo=utc)
    x_max = x_max.replace(year=x_year_max, month=x_month_max, day=x_day_max, hour=x_hour_max, minute=x_min_max, second=x_sec_max, microsecond=0, tzinfo=utc)

    grb_set = []
    grb_table_data = measurement.objects.all().order_by('grb_name')
    #grb_table = measurement.objects.filter(date__range = (x_min, x_max)).order_by('grb_name')

    grb_table = []
    for item in grb_table_data:
        if (item.date >= x_min) and (item.date <= x_max):
            grb_table.append(item)

    for item in grb_table:
        grb_set.append(item.grb_name.grb_name)

    cut_array = []
    for i in range(0, int(num_cuts), 1):
        cut_row = []
        cut_row.append(str('cut_')+str(i)+'_min')
        cut_row.append(str('cut_')+str(i))
        cut_row.append(str('cut_')+str(i)+'_max')
        #cut_row.append('') # cut min value (index - 3)
        #cut_row.append('') # cut max value (index - 4)
        #cut_row.append('') # cut variable  (index - 5)
        commnd_str = "cut_row.append(request.GET.get('cut_" + str(i) + "_min' , '0'))" # cut min value (index - 3)
        exec commnd_str
        commnd_str = "cut_row.append(request.GET.get('cut_" + str(i) + "_max' , '2'))" # cut max value (index - 4)
        exec commnd_str
        commnd_str = "cut_row.append(request.GET.get('cut_" + str(i) + "' , r'BAT T90'))" # cut variable (index - 5)
        exec commnd_str
        cut_array.append(cut_row)
    parameters.append(cut_array)

    cut_set = []
    if num_cuts > 0:
        for cut_item in cut_array:
            grb_sub_set = []
            cut_value_min = float(cut_item[3])
            cut_value_max = float(cut_item[4])
            #import pdb; pdb.set_trace() # debugging code
            cut_measurement_type = measurement_type.objects.get(measurement_type_name=cut_item[5])
            cut_measurement = []
            for mitem in grb_table_data:
                if (mitem.measurement_type == cut_measurement_type) and (mitem.value <= cut_value_max) and (mitem.value >= cut_value_min):
                    cut_measurement.append(mitem)
            #cut_measurement = measurement.objects.filter(measurement_type=cut_measurement_type, value__lte=cut_value_max, value__gte=cut_value_min)
            cut_set.append(cut_measurement_type.measurement_type_id)
            for item in cut_measurement:
                grb_sub_set.append(item.grb_name.grb_name)
            grb_set = get_set_intersection(grb_set, grb_sub_set)
            #import pdb; pdb.set_trace() # debugging code

    return grb_set, parameters

def get_grb_sample(request):
    parameters = []
    year = timedelta(days=365)
    week = timedelta(days=7)
    day = timedelta(days=1)
    cur_time = datetime.utcnow()
    #cur_time = cur_time.replace(year=cur_time.year, month=cur_time.month, day=cur_time.day, hour=cur_time.hour, minute=cur_time.minute, second=cur_time.second, microsecond=0, tzinfo=utc)
    #default_date = cur_time - week
    cur_time = cur_time.replace(year=cur_time.year, month=cur_time.month, day=cur_time.day, hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)
    default_date = cur_time - (week * 48)

    num_cuts = request.GET.get('num_cuts', 0)
    parameters.append(num_cuts)
    no_date_cut = request.GET.get('no_date_cut', 'False')
    parameters.append(no_date_cut)

    x_year_min = int(request.GET.get('x_year_min', default_date.year))
    parameters.append(x_year_min)
    x_month_min = int(request.GET.get('x_month_min', default_date.month))
    parameters.append(x_month_min)
    x_day_min = int(request.GET.get('x_day_min', default_date.day))
    parameters.append(x_day_min)
    x_hour_min = int(request.GET.get('x_hour_min', default_date.hour))
    parameters.append(x_hour_min)
    x_min_min = int(request.GET.get('x_min_min', default_date.minute))
    parameters.append(x_min_min)
    x_sec_min = int(request.GET.get('x_sec_min', default_date.second))
    parameters.append(x_sec_min)

    x_year_max = int(request.GET.get('x_year_max', cur_time.year))
    parameters.append(x_year_max)
    x_month_max = int(request.GET.get('x_month_max', cur_time.month))
    parameters.append(x_month_max)
    x_day_max = int(request.GET.get('x_day_max', cur_time.day))
    parameters.append(x_day_max)
    x_hour_max = int(request.GET.get('x_hour_max', cur_time.hour))
    parameters.append(x_hour_max)
    x_min_max = int(request.GET.get('x_min_max', cur_time.minute))
    parameters.append(x_min_max)
    x_sec_max = int(request.GET.get('x_sec_max', cur_time.second))
    parameters.append(x_sec_max)

    x_min = datetime.utcnow()
    x_max = datetime.utcnow()

    if no_date_cut == 'True':
        x_year_min = 1900
        x_year_max = 2100

    x_min = x_min.replace(year=x_year_min, month=x_month_min, day=x_day_min, hour=x_hour_min, minute=x_min_min, second=x_sec_min, microsecond=0, tzinfo=utc)
    x_max = x_max.replace(year=x_year_max, month=x_month_max, day=x_day_max, hour=x_hour_max, minute=x_min_max, second=x_sec_max, microsecond=0, tzinfo=utc)

    data_file = open(grb_data_file, 'rb')
    grb_data_table = cPickle.load(data_file)
    data_file.close()

    #for item in grb_data_table:
    #    print item
    #    import ipdb; ipdb.set_trace() # debugging code

    #import ipdb; ipdb.set_trace() # debugging code
    #print grb_data_table

    #grb_table_data = measurement.objects.all().order_by('grb_name')
    #grb_table = measurement.objects.filter(date__range = (x_min, x_max)).order_by('grb_name')

    sortdownStr = str(request.GET.get('sort_down', 'GRB Date'))
    if sortdownStr=='GRB':
        sortdownStr = 'GRB Date'

    command_str = "grb_data_table = sorted(grb_data_table, key=lambda grb_data_table:grb_data_table['" + sortdownStr + "'], reverse=True)"
    exec command_str

    sortupStr = str(request.GET.get('sort_up', ''))
    if sortupStr=='GRB':
        sortupStr = 'GRB Date'
    if len(sortupStr) > 0:
        command_str = "grb_data_table = sorted(grb_data_table, key=lambda grb_data_table:grb_data_table['" + sortupStr + "'])"
        exec command_str

    #grb_data_table = sorted(grb_data_table, key=lambda grb_data_table:grb_data_table['GRB Date'], reverse=True)

    # make the date cut on the GRB data
    grb_table = []
    for item in grb_data_table:
        grb_date = item['GRB Date']
        if (grb_date >= x_min) and (grb_date <= x_max):
            grb_table.append(item)

    #print len(grb_table)
    #import ipdb; ipdb.set_trace() # debugging code

    # setup various cuts specified by the user
    cut_array = []
    for i in range(0, int(num_cuts), 1):
        cut_row = []
        cut_row.append(str('cut_')+str(i)+'_min')
        cut_row.append(str('cut_')+str(i))
        cut_row.append(str('cut_')+str(i)+'_max')
        #cut_row.append('') # cut min value (index - 3)
        #cut_row.append('') # cut max value (index - 4)
        #cut_row.append('') # cut variable  (index - 5)
        commnd_str = "cut_row.append(request.GET.get('cut_" + str(i) + "_min' , '0'))" # cut min value (index - 3)
        exec commnd_str
        commnd_str = "cut_row.append(request.GET.get('cut_" + str(i) + "_max' , '2'))" # cut max value (index - 4)
        exec commnd_str
        commnd_str = "cut_row.append(request.GET.get('cut_" + str(i) + "' , r'BAT T90'))" # cut variable (index - 5)
        exec commnd_str
        cut_array.append(cut_row)
    parameters.append(cut_array)

    # make various cuts as specified by the user
    selected_grb_set = grb_table
    if num_cuts > 0:
        for cut_item in cut_array:
            grb_sub_set = []
            cut_value_min = float(cut_item[3])
            cut_value_max = float(cut_item[4])
            cut_measurement_type = str(cut_item[5])
            for mitem in selected_grb_set:
                #import ipdb; ipdb.set_trace() # debugging code
                if (mitem[cut_measurement_type] <= cut_value_max) and (mitem[cut_measurement_type] >= cut_value_min):
                    grb_sub_set.append(mitem)
            selected_grb_set = grb_sub_set
            #import ipdb; ipdb.set_trace() # debugging code
    #print "Selected GRBs = ", len(selected_grb_set)
    #import ipdb; ipdb.set_trace() # debugging code

    return selected_grb_set, parameters

def select_grb_sample(request):

    # get the GRB sample after all the cuts
    grb_set, parameters = get_grb_sample(request)

    #import pdb; pdb.set_trace() # debugging code
    #grb_table = grb.objects.filter(date__range = (x_min, x_max))


    # determine measurement type that can be used for cuts
    #import ipdb; ipdb.set_trace() # debugging code
    #for key, value in grb_set[0].items():
    #    if str(type(value)).find('float') > 0:
    #        available_cut_types.append(key)

    # Determine measurement types that needs to be displayed in the bottom selected GRB table
    #available_measurement_types = grb_set[0].keys()
    #available_measurement_types.remove('GRB Name')
    #available_measurement_types.remove('GRB Date')
    measurement_type_ = measurement_type.objects.all()
    available_measurement_types = []
    available_cut_types = []
    for item in measurement_type_:
        available_measurement_types.append(item.measurement_type_name)
        if item.data_type == 'FLOAT':
            available_cut_types.append(item.measurement_type_name)
    type_set = []
    available_types = []
    type_id = 0
    for type_name in available_measurement_types:
        type_row = []  # this list will have three elements to indicate type id, name and check status
        type_row.append("type_"+str(type_id))
        type_row.append(type_name)
        display = ''
        commnd_str = "display=request.GET.get('type_" + str(type_id) + "' , 'False')"
        exec commnd_str
        if display == 'True':
            type_set.append(type_id)
            type_row.append('True')  # this is used to identify which checkboxes to check in the control panel
        else:
            type_row.append('False')
        type_row.append(type_id)
        available_types.append(type_row)
        type_id += 1

    # if there are no measurement types selected for display then set some default set
    if len(type_set) == 0:
        #type_set = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
        #type_set = [2, 3, 4, 6, 7, 8, 13, 28, 30]
        type_set = [1, 2, 3, 5, 6, 7, 12, 27, 29]
        for item in type_set:
            available_types[item][2] = 'True'

    grb_table_header = []
    grb_table_header_col = []
    grb_table_header_col.append('GRB')  # measurement name
    grb_table_header_col.append('')  # units
    grb_table_header_col.append(0)  # float?
    grb_table_header_col.append(0) # id
    grb_table_header.append(grb_table_header_col)
    for col_item in available_types:
        if col_item[2] == 'True':
            #grb_measurement = grb_set[0][col_item[1]]
            grb_table_header_col = []
            grb_table_header_col.append(col_item[1]) # measurement name
            grb_table_header_col.append(measurement_type.objects.get(measurement_type_name=col_item[1]).units) # units
            if measurement_type.objects.get(measurement_type_name=col_item[1]).data_type == 'FLOAT': # float?
                grb_table_header_col.append(1)
            else:
                grb_table_header_col.append(0)
            #print col_item[3], str(type(grb_measurement)), col_item[1]
            #import ipdb; ipdb.set_trace() # debugging code
            grb_table_header_col.append(col_item[3]) # id
            grb_table_header.append(grb_table_header_col)

    # set up the final GRB table for display
    grb_data = []
    for grb_item in grb_set:
        grb_data_row = []
        grb_data_row.append(grb_item['GRB Name'])
        for col_item in available_types:
            if col_item[2] == 'True':
                grb_measurement = grb_item[col_item[1]]
                grb_data_row.append(grb_measurement)
        grb_data.append(grb_data_row)

    number_of_rows = len(grb_data)

    return grb_data, grb_table_header, number_of_rows, available_types, available_cut_types, parameters

def grb_main_page(request):

    grb_data, grb_table_header, number_of_rows, available_types, available_cut_types, parameters = select_grb_sample(request)

    return render_to_response('grb_main_page.html', {'grb_data':grb_data,
                                                     'grb_table_header':grb_table_header,
                                                     'number_of_rows':number_of_rows,
                                                     'available_types':available_types,
                                                     'available_cut_types':available_cut_types,
                                                     'num_cuts':parameters[0],
                                                     'no_date_cut':parameters[1],
                                                     'x_year_min':parameters[2],
                                                     'x_month_min':parameters[3],
                                                     'x_day_min':parameters[4],
                                                     'x_hour_min':parameters[5],
                                                     'x_min_min':parameters[6],
                                                     'x_sec_min':parameters[7],
                                                     'x_year_max':parameters[8],
                                                     'x_month_max':parameters[9],
                                                     'x_day_max':parameters[10],
                                                     'x_hour_max':parameters[11],
                                                     'x_min_max':parameters[12],
                                                     'x_sec_max':parameters[13],
                                                     'cut_array':parameters[14],
    })

def download_data(request):

    grb_data, grb_table_header, number_of_rows, available_types, available_cut_types, parameters = select_grb_sample(request)

    num = len(grb_data)

    grb_header = []
    for header_item in grb_table_header:
        grb_header.append(header_item[0])

    #import ipdb; ipdb.set_trace() # debugging code

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename="grb_data.csv"'
    writer = csv.writer(response)
    if num > 0:
        writer.writerow(grb_header)
        for row in grb_data:
            writer.writerow(row)
    else:
        writer.writerow(["No data!"])

    return response


def histo_page(request):

    # this variable is used for communicate error to the client

    m_type = str(request.GET.get('measurement_type', 'T90'))

    grb_set, parameters = get_grb_sample(request)

    x_label = request.GET.get('x_label', m_type)
    y_label = request.GET.get('y_label', 'Frequency')
    title = request.GET.get('title', 'Histogram of ' + m_type)
    bin_num = request.GET.get('bin_num', '25')

    x_min = request.GET.get('x_min',0)
    x_max = request.GET.get('x_max',0)
    y_min = request.GET.get('y_min',0)
    y_max = request.GET.get('y_max',0)
    x_log = request.GET.get('x_log', 'False')
    y_log = request.GET.get('y_log', 'False')

    #import pdb; pdb.set_trace() # debugging code

    return render_to_response('histo_page.html', {#'measurement_data':measurement_data,
                                                     'measurement_type':m_type,
                                                     'bin_num':bin_num,
                                                     'num_cuts':parameters[0],
                                                     'no_date_cut':parameters[1],
                                                     'x_year_min':parameters[2],
                                                     'x_month_min':parameters[3],
                                                     'x_day_min':parameters[4],
                                                     'x_hour_min':parameters[5],
                                                     'x_min_min':parameters[6],
                                                     'x_sec_min':parameters[7],
                                                     'x_year_max':parameters[8],
                                                     'x_month_max':parameters[9],
                                                     'x_day_max':parameters[10],
                                                     'x_hour_max':parameters[11],
                                                     'x_min_max':parameters[12],
                                                     'x_sec_max':parameters[13],
                                                     'cut_array':parameters[14],
                                                     'x_label':x_label,
                                                     'y_label':y_label,
                                                     'title':title,
                                                     'x_min':x_min,
                                                     'x_max':x_max,
                                                     'y_min':y_min,
                                                     'y_max':y_max,
                                                     'x_log':x_log,
                                                     'y_log':y_log,
    })

def histo(request):

    fig = Figure(figsize=(12, 7), edgecolor='white', facecolor='white')
    fig.subplots_adjust(top=0.95)
    fig.subplots_adjust(bottom=0.07)
    fig.subplots_adjust(left=0.06)
    fig.subplots_adjust(right=0.98)

    plot_type = request.GET.get('plot_type', 'png')
    bin_num = int(request.GET.get('bin_num', '25'))
    m_type = str(request.GET.get('measurement_type', 'T90'))

    grb_set, parameters = get_grb_sample(request)

    #import ipdb; ipdb.set_trace() # debugging code

    # following code will improve the plotting speed...
    measurement_type_item = measurement_type.objects.filter(measurement_type_name = m_type)
    unit = measurement_type_item[0].units

    #measurement_table = measurement.objects.filter(measurement_type=measurement_type_item[0])
    #import pdb; pdb.set_trace() # debugging code

    x_log = request.GET.get('x_log', 'False')
    y_log = request.GET.get('y_log', 'False')

    x = []
    for item in grb_set:
        measurement_value = item[m_type]
        if measurement_value != '-':
            if (measurement_value > 0) and (x_log == 'True'):
                x.append(math.log10(measurement_value))
            else:
                x.append(measurement_value)
    #print x
    #import ipdb; ipdb.set_trace() # debugging code
    #import numpy as np
    #x = np.random.randn(1000)
    num_points = len(x)
    sample_size_str = " (Number of GRBs: " + str(num_points) + ")"

    if (x_log == 'True'):
        if len(unit) > 1:
            if unit != 'None':
                x_label = 'log ' + request.GET.get('x_label', m_type) + ' (' + unit + ')'
            else:
                x_label = 'log ' + request.GET.get('x_label', m_type)
        else:
            x_label = 'log ' + request.GET.get('x_label', m_type)
    else:
        if len(unit) > 1:
            if unit != 'None':
                x_label = request.GET.get('x_label', m_type) + ' (' + unit + ')'
            else:
                x_label = request.GET.get('x_label', m_type)
        else:
            x_label = request.GET.get('x_label', m_type)
    y_label = request.GET.get('y_label', 'Counts')
    title = request.GET.get('title', 'Histogram') + sample_size_str

    ax=fig.add_subplot(111)
    #ax.plot(x, y, 'r', linewidth=2.0)

    #n, bins, patches = ax.hist(x, 50, normed=1, facecolor='green', alpha=0.75)
    if (y_log == 'True'):
        n, bins, patches = ax.hist(x, bin_num, facecolor='green', alpha=0.75, log=True)
    else:
        n, bins, patches = ax.hist(x, bin_num, facecolor='green', alpha=0.75)

    x_scale_min = int(request.GET.get('x_min', 0))
    x_scale_max = int(request.GET.get('x_max', 0))
    y_scale_min = int(request.GET.get('y_min', 0))
    y_scale_max = int(request.GET.get('y_max', 0))

    if (x_scale_min <  x_scale_max) and (y_scale_min <  y_scale_max):
        #import pdb; pdb.set_trace() # debugging code
        ax.axis([x_scale_min, x_scale_max, y_scale_min, y_scale_max])


    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    #import ipdb; ipdb.set_trace() # debugging code
    statistics_str = "Mean : {0:.3} \nStd. Deviation : {1:.3}".format(ds.mean(x), ds.std(x))
    #print statistics_str
    ax.text(0.05, 0.9, statistics_str,
        fontsize=15,
        #color='blue',
        bbox={'facecolor':'yellow', 'pad':10, 'alpha':0.65},
        horizontalalignment='left',
        verticalalignment='center',
        transform = ax.transAxes)

    canvas=FigureCanvas(fig)

    if plot_type == 'png':
        response=HttpResponse(content_type='image/png')
        canvas.print_png(response)

    if plot_type == 'pdf':
        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="histo.pdf"'
        #response=django.http.HttpResponse(content_type='image/pdf')
        #response=['Content-Disposition'] = 'attachment; filename=plot.pdf'
        canvas = PdfFigureCanvas(fig)
        canvas.print_pdf(response)


    if plot_type == 'text':
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename="histo.csv"'
        writer = csv.writer(response)
        if len(n) > 0:
            writer.writerow(['Counts'])
            for i in range(len(n)):
                writer.writerow([n[i]])
            writer.writerow(['Bins'])
            for i in range(len(bins)):
                writer.writerow([bins[i]])
        else:
            writer.writerow(["No data!"])

    return response

def corr_page(request):

    # this variable is used for communicate error to the client
    #error = False
    #mtype = str(request.GET.get('measurement_type', 'T90'))

    grb_set, parameters = get_grb_sample(request)

    x_min = request.GET.get('x_min',0)
    x_max = request.GET.get('x_max',0)
    y_min = request.GET.get('y_min',0)
    y_max = request.GET.get('y_max',0)
    x_log = request.GET.get('x_log', 'False')
    y_log = request.GET.get('y_log', 'False')

    available_types = []
    available_measurement_types = measurement_type.objects.all()
    for item in available_measurement_types:
        if item.data_type == 'FLOAT':
            type_row = []
            type_row.append(item.measurement_type_id)
            type_row.append(item.measurement_type_name)
            available_types.append(type_row)

    type_id_01 = request.GET.get('type_id_01', available_types[0][1])
    type_id_02 = request.GET.get('type_id_02', available_types[1][1])

    c_label = request.GET.get('c_label', "False")
    if c_label == "True":
        x_label = request.GET.get('x_label', type_id_01)
        y_label = request.GET.get('y_label', type_id_02)
        title = request.GET.get('title', type_id_01 + " vs. " + type_id_02)
    else:
        x_label = type_id_01
        y_label = type_id_02
        title = type_id_01 + " vs. " + type_id_02

    #print available_types
    #import pdb; pdb.set_trace() # debugging code

    return render_to_response('corr_page.html', {'available_types':available_types,
                                                     'type_id_01':type_id_01,
                                                     'type_id_02':type_id_02,
                                                     'num_cuts':parameters[0],
                                                     'no_date_cut':parameters[1],
                                                     'x_year_min':parameters[2],
                                                     'x_month_min':parameters[3],
                                                     'x_day_min':parameters[4],
                                                     'x_hour_min':parameters[5],
                                                     'x_min_min':parameters[6],
                                                     'x_sec_min':parameters[7],
                                                     'x_year_max':parameters[8],
                                                     'x_month_max':parameters[9],
                                                     'x_day_max':parameters[10],
                                                     'x_hour_max':parameters[11],
                                                     'x_min_max':parameters[12],
                                                     'x_sec_max':parameters[13],
                                                     'cut_array':parameters[14],
                                                     'c_label':c_label,
                                                     'x_label':x_label,
                                                     'y_label':y_label,
                                                     'title':title,
                                                     'x_min':x_min,
                                                     'x_max':x_max,
                                                     'y_min':y_min,
                                                     'y_max':y_max,
                                                     'x_log':x_log,
                                                     'y_log':y_log,
    })

def corr_plot(request):

    fig = Figure(figsize=(12, 7), edgecolor='white', facecolor='white')
    fig.subplots_adjust(top=0.95)
    fig.subplots_adjust(bottom=0.07)
    fig.subplots_adjust(left=0.06)
    fig.subplots_adjust(right=0.98)

    plot_type = request.GET.get('plot_type', 'png')

    available_types = []
    available_measurement_types = measurement_type.objects.all()
    for item in available_measurement_types:
        if item.data_type == 'FLOAT':
            type_row = []
            type_row.append(item.measurement_type_id)
            type_row.append(item.measurement_type_name)
            available_types.append(type_row)

    type_id_01 = request.GET.get('type_id_01', available_types[0][1])
    type_id_02 = request.GET.get('type_id_02', available_types[1][1])

    #import pdb; pdb.set_trace() # debugging code

    measurement_type_item1 = measurement_type.objects.filter(measurement_type_name = type_id_01)
    measurement_type_item2 = measurement_type.objects.filter(measurement_type_name = type_id_02)
    unit1 = measurement_type_item1[0].units
    unit2 = measurement_type_item2[0].units

    # This is the grb subset that passes all the user cuts...
    #grb_table = measurement.objects.filter(date__range = (x_min, x_max)) # there can be duplicates here...need to fix this later

    grb_set, parameters = get_grb_sample(request)

    # both measurements must have same number of rows...
    # if one item is missing then the other item should be ignored...
    x_log = request.GET.get('x_log', 'False')
    y_log = request.GET.get('y_log', 'False')

    x = []
    y = []
    for grb_item in grb_set:
        measurement_value1 = grb_item[type_id_01]
        measurement_value2 = grb_item[type_id_02]
        if (measurement_value1 != '-') and (measurement_value2 != '-'):
            if (measurement_value1 > 0) and (x_log == 'True'):
                x.append(math.log10(measurement_value1))
            else:
                x.append(measurement_value1)
            if (measurement_value2 > 0) and (y_log == 'True'):
                y.append(math.log10(measurement_value2))
            else:
                y.append(measurement_value2)

    #print x
    #print y
    #import pdb; pdb.set_trace() # debugging code
    #import numpy as np
    #x = np.random.randn(1000)

    if x_log == 'True':
        if len(unit1) > 1:
            if unit1 != 'None':
                x_label = 'log ' + request.GET.get('x_label', type_id_01) + ' (' + unit1 + ')'
            else:
                x_label = 'log ' + request.GET.get('x_label', type_id_01)
        else:
            x_label = 'log ' + request.GET.get('x_label', type_id_01)

    else:
        if len(unit1) > 1:
            if unit1 != 'None':
                x_label = request.GET.get('x_label', type_id_01) + ' (' + unit1 + ')'
            else:
                x_label = request.GET.get('x_label', type_id_01)
        else:
            x_label = request.GET.get('x_label', type_id_01)

    if y_log == 'True':
        if len(unit2) > 1:
            if unit2 != 'None':
                y_label = 'log ' + request.GET.get('y_label', type_id_02) + ' (' + unit2 + ')'
            else:
                y_label = 'log ' + request.GET.get('y_label', type_id_02)
        else:
            y_label = 'log ' + request.GET.get('y_label', type_id_02)

    else:
        if len(unit2) > 1:
            if unit2 != 'None':
                y_label = request.GET.get('y_label', type_id_02) + ' (' + unit2 + ')'
            else:
                y_label = request.GET.get('y_label', type_id_02)
        else:
            y_label = request.GET.get('y_label', type_id_02)

    num_points = len(x)
    sample_size_str = " (Number of GRBs: " + str(num_points) + ")"

    title = request.GET.get('title', 'Correlation Plot') + sample_size_str

    ax=fig.add_subplot(111)
    ax.plot(x, y, 'ro')

    #n, bins, patches = ax.hist(x, 50, normed=1, facecolor='green', alpha=0.75)
    #if (y_log == 'True'):
    #    n, bins, patches = ax.hist(x, bin_num, facecolor='green', alpha=0.75, log=True)
    #else:
    #    n, bins, patches = ax.hist(x, bin_num, facecolor='green', alpha=0.75)

    #import pdb; pdb.set_trace() # debugging code

    x_scale_min = int(request.GET.get('x_min', 0))
    x_scale_max = int(request.GET.get('x_max', 0))
    y_scale_min = int(request.GET.get('y_min', 0))
    y_scale_max = int(request.GET.get('y_max', 0))

    if (x_scale_min <  x_scale_max) and (y_scale_min <  y_scale_max):
        #import pdb; pdb.set_trace() # debugging code
        ax.axis([x_scale_min, x_scale_max, y_scale_min, y_scale_max])


    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    #import ipdb; ipdb.set_trace() # debugging code
    statistics_str = "Correlation Coefficient : {0:.3}".format(ds.corr(x, y))
    #print statistics_str
    ax.text(0.05, 0.9, statistics_str,
        fontsize=15,
        #color='blue',
        bbox={'facecolor':'yellow', 'pad':10, 'alpha':0.65},
        horizontalalignment='left',
        verticalalignment='center',
        transform = ax.transAxes)

    canvas=FigureCanvas(fig)

    if plot_type == 'png':
        response=HttpResponse(content_type='image/png')
        canvas.print_png(response)

    if plot_type == 'pdf':
        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="histo.pdf"'
        #response=django.http.HttpResponse(content_type='image/pdf')
        #response=['Content-Disposition'] = 'attachment; filename=plot.pdf'
        canvas = PdfFigureCanvas(fig)
        canvas.print_pdf(response)


    if plot_type == 'text':
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename="plot.csv"'
        writer = csv.writer(response)
        if num_points > 0:
            writer.writerow(['X Values'])
            for i in range(num_points):
                writer.writerow([x[i]])
            writer.writerow(['Y Values'])
            for i in range(num_points):
                writer.writerow([y[i]])
        else:
            writer.writerow(["No data!"])

    return response

def plot_3d_page(request):

    # this variable is used for communicate error to the client
    #error = False
    #mtype = str(request.GET.get('measurement_type', 'T90'))

    grb_set, parameters = get_grb_sample(request)

    x_min = request.GET.get('x_min',0)
    x_max = request.GET.get('x_max',0)
    y_min = request.GET.get('y_min',0)
    y_max = request.GET.get('y_max',0)
    x_log = request.GET.get('x_log', 'False')
    y_log = request.GET.get('y_log', 'False')

    available_types = []
    available_measurement_types = measurement_type.objects.all()
    for item in available_measurement_types:
        if item.data_type == 'FLOAT':
            type_row = []
            type_row.append(item.measurement_type_id)
            type_row.append(item.measurement_type_name)
            available_types.append(type_row)

    type_id_01 = request.GET.get('type_id_01', available_types[0][1])
    type_id_02 = request.GET.get('type_id_02', available_types[1][1])

    c_label = request.GET.get('c_label', "False")
    if c_label == "True":
        x_label = request.GET.get('x_label', type_id_01)
        y_label = request.GET.get('y_label', type_id_02)
        title = request.GET.get('title', type_id_01 + " vs. " + type_id_02)
    else:
        x_label = type_id_01
        y_label = type_id_02
        title = type_id_01 + " vs. " + type_id_02

    #print available_types
    #import pdb; pdb.set_trace() # debugging code

    return render_to_response('corr_page.html', {'available_types':available_types,
                                                     'type_id_01':type_id_01,
                                                     'type_id_02':type_id_02,
                                                     'num_cuts':parameters[0],
                                                     'no_date_cut':parameters[1],
                                                     'x_year_min':parameters[2],
                                                     'x_month_min':parameters[3],
                                                     'x_day_min':parameters[4],
                                                     'x_hour_min':parameters[5],
                                                     'x_min_min':parameters[6],
                                                     'x_sec_min':parameters[7],
                                                     'x_year_max':parameters[8],
                                                     'x_month_max':parameters[9],
                                                     'x_day_max':parameters[10],
                                                     'x_hour_max':parameters[11],
                                                     'x_min_max':parameters[12],
                                                     'x_sec_max':parameters[13],
                                                     'cut_array':parameters[14],
                                                     'c_label':c_label,
                                                     'x_label':x_label,
                                                     'y_label':y_label,
                                                     'title':title,
                                                     'x_min':x_min,
                                                     'x_max':x_max,
                                                     'y_min':y_min,
                                                     'y_max':y_max,
                                                     'x_log':x_log,
                                                     'y_log':y_log,
    })

def plot_3d(request):

    fig = Figure(figsize=(12, 7), edgecolor='white', facecolor='white')
    fig.subplots_adjust(top=0.95)
    fig.subplots_adjust(bottom=0.07)
    fig.subplots_adjust(left=0.06)
    fig.subplots_adjust(right=0.98)

    plot_type = request.GET.get('plot_type', 'png')

    available_types = []
    available_measurement_types = measurement_type.objects.all()
    for item in available_measurement_types:
        if item.data_type == 'FLOAT':
            type_row = []
            type_row.append(item.measurement_type_id)
            type_row.append(item.measurement_type_name)
            available_types.append(type_row)

    type_id_01 = request.GET.get('type_id_01', available_types[0][1])
    type_id_02 = request.GET.get('type_id_02', available_types[1][1])

    #import pdb; pdb.set_trace() # debugging code

    measurement_type_item1 = measurement_type.objects.filter(measurement_type_name = type_id_01)
    measurement_type_item2 = measurement_type.objects.filter(measurement_type_name = type_id_02)
    unit1 = measurement_type_item1[0].units
    unit2 = measurement_type_item2[0].units

    # This is the grb subset that passes all the user cuts...
    #grb_table = measurement.objects.filter(date__range = (x_min, x_max)) # there can be duplicates here...need to fix this later

    grb_set, parameters = get_grb_sample(request)

    # both measurements must have same number of rows...
    # if one item is missing then the other item should be ignored...
    x_log = request.GET.get('x_log', 'False')
    y_log = request.GET.get('y_log', 'False')

    x = []
    y = []
    for grb_item in grb_set:
        measurement_value1 = grb_item[type_id_01]
        measurement_value2 = grb_item[type_id_02]
        if (measurement_value1 != '-') and (measurement_value2 != '-'):
            if (measurement_value1 > 0) and (x_log == 'True'):
                x.append(math.log10(measurement_value1))
            else:
                x.append(measurement_value1)
            if (measurement_value2 > 0) and (y_log == 'True'):
                y.append(math.log10(measurement_value2))
            else:
                y.append(measurement_value2)

    #print x
    #print y
    #import pdb; pdb.set_trace() # debugging code
    #import numpy as np
    #x = np.random.randn(1000)

    if x_log == 'True':
        if len(unit1) > 1:
            if unit1 != 'None':
                x_label = 'log ' + request.GET.get('x_label', type_id_01) + ' (' + unit1 + ')'
            else:
                x_label = 'log ' + request.GET.get('x_label', type_id_01)
        else:
            x_label = 'log ' + request.GET.get('x_label', type_id_01)

    else:
        if len(unit1) > 1:
            if unit1 != 'None':
                x_label = request.GET.get('x_label', type_id_01) + ' (' + unit1 + ')'
            else:
                x_label = request.GET.get('x_label', type_id_01)
        else:
            x_label = request.GET.get('x_label', type_id_01)

    if y_log == 'True':
        if len(unit2) > 1:
            if unit2 != 'None':
                y_label = 'log ' + request.GET.get('y_label', type_id_02) + ' (' + unit2 + ')'
            else:
                y_label = 'log ' + request.GET.get('y_label', type_id_02)
        else:
            y_label = 'log ' + request.GET.get('y_label', type_id_02)

    else:
        if len(unit2) > 1:
            if unit2 != 'None':
                y_label = request.GET.get('y_label', type_id_02) + ' (' + unit2 + ')'
            else:
                y_label = request.GET.get('y_label', type_id_02)
        else:
            y_label = request.GET.get('y_label', type_id_02)

    num_points = len(x)
    sample_size_str = " (Number of GRB: " + str(num_points) + ")"

    title = request.GET.get('title', 'Correlation Plot') + sample_size_str

    ax=fig.add_subplot(111)
    ax.plot(x, y, 'ro')

    #n, bins, patches = ax.hist(x, 50, normed=1, facecolor='green', alpha=0.75)
    #if (y_log == 'True'):
    #    n, bins, patches = ax.hist(x, bin_num, facecolor='green', alpha=0.75, log=True)
    #else:
    #    n, bins, patches = ax.hist(x, bin_num, facecolor='green', alpha=0.75)

    #import pdb; pdb.set_trace() # debugging code

    x_scale_min = int(request.GET.get('x_min', 0))
    x_scale_max = int(request.GET.get('x_max', 0))
    y_scale_min = int(request.GET.get('y_min', 0))
    y_scale_max = int(request.GET.get('y_max', 0))

    if (x_scale_min <  x_scale_max) and (y_scale_min <  y_scale_max):
        #import pdb; pdb.set_trace() # debugging code
        ax.axis([x_scale_min, x_scale_max, y_scale_min, y_scale_max])


    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    #import ipdb; ipdb.set_trace() # debugging code
    statistics_str = "Correlation Coefficient : {0:.3}".format(ds.corr(x, y))
    #print statistics_str
    ax.text(0.05, 0.9, statistics_str,
        fontsize=15,
        #color='blue',
        bbox={'facecolor':'yellow', 'pad':10, 'alpha':0.65},
        horizontalalignment='left',
        verticalalignment='center',
        transform = ax.transAxes)

    canvas = FigureCanvas(fig)

    if plot_type == 'png':
        response=HttpResponse(content_type='image/png')
        canvas.print_png(response)

    if plot_type == 'pdf':
        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="histo.pdf"'
        #response=django.http.HttpResponse(content_type='image/pdf')
        #response=['Content-Disposition'] = 'attachment; filename=plot.pdf'
        canvas = PdfFigureCanvas(fig)
        canvas.print_pdf(response)

    if plot_type == 'text':
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename="plot.csv"'
        writer = csv.writer(response)
        if num_points > 0:
            writer.writerow(['X Values'])
            for i in range(num_points):
                writer.writerow([x[i]])
            writer.writerow(['Y Values'])
            for i in range(num_points):
                writer.writerow([y[i]])
        else:
            writer.writerow(["No data!"])

    return response

def help_page(request):

    help_topic = request.GET.get('help_topic', 'grb_catalog_main_help')
    help_info = help.objects.get(name=help_topic)

    title_str = help_info.title
    description_str = help_info.description

    #print available_types
    #import pdb; pdb.set_trace() # debugging code

    return render_to_response('help_page.html', {'title': title_str,
                                                 'description': description_str,
    })

def grb_page(request):

    grb_name = request.GET.get('grb_name', '')

    grb_entry = grb.objects.filter(grb_name = grb_name)
    m_data = measurement.objects.filter(grb_name = grb_entry).order_by('measurement_type')

    measurement_data = []

    for item in m_data:
        mea_row = []
        mea_row.append(item.measurement_type.measurement_type_name)
        if item.measurement_type.data_type == 'FLOAT':
            mea_row.append(str(item.value))
        if item.measurement_type.data_type == 'TEXT':
            mea_row.append(item.text)
        if item.measurement_type.data_type == 'DATE':
            mea_row.append(item.date)
        mea_row.append(item.measurement_id)
        mea_row.append(str(item.measurement_type.units))
        measurement_data.append(mea_row)

    #print measurement_data
    #import ipdb; ipdb.set_trace() # debugging code

    return render_to_response('grb_page.html', {'grb_name': grb_name,
                                                 'measurement_data': measurement_data,
    })

def machine_z_page(request):

    grb_name = request.GET.get('grb_name', "")

    key_map_df = pandas.read_csv(feature_key_map)
    key_map_header = key_map_df.columns
    measurement_data = []

    for index, row in key_map_df.iterrows():
        #print row[key_map_header[0]], row[key_map_header[1]], row[key_map_header[2]]
        measurement_row = []
        measurement_row.append(row[key_map_header[0]])  # feature name
        measurement_row.append(row[key_map_header[2]])  # value
        measurement_row.append(str(row[key_map_header[1]]).strip()) # key
        measurement_row.append(row[key_map_header[3]])  # used in machine-z
        measurement_row.append(row[key_map_header[4]])  # used in high-z classifier
        if row[key_map_header[3]] == 0 and row[key_map_header[4]] == 0:
            measurement_row.append(0)  # don't show the row
        else:
            measurement_row.append(1)  # show the row
        measurement_data.append(measurement_row)

    #import ipdb; ipdb.set_trace() # debugging code

    show_highz = 0
    highz_results = []
    feature_list = []
    for measurement_item in measurement_data:
        feature = float(request.GET.get(measurement_item[2], -1000.0))
        #import ipdb; ipdb.set_trace() # debugging code
        measurement_item[1] = feature
        feature_list.append(feature)
        if feature > -1000.0:
            show_highz = 1

    if show_highz > 0:
        feature_list = np.array(feature_list)
        highz_results = machinez.get_highz_information(feature_list)

    #import ipdb; ipdb.set_trace() # debugging code

    return render_to_response('machine_z_page.html', {'grb_name': grb_name,
                                                      'measurement_data': measurement_data,
                                                      'highz_results': highz_results,
                                                      'show_highz': show_highz,
    })

#@login_required(login_url=login_url)
def gpose_sim_page(request):

    gpose_para_df = pandas.read_csv(gpose_sim_parameters)
    gpose_para_header = gpose_para_df.columns
    sim_parameters = []
    sim_parameters_dict = {}

    for index, row in gpose_para_df.iterrows():
        #print row[key_map_header[0]], row[key_map_header[1]], row[key_map_header[2]]
        sim_parameters_row = []
        sim_parameters_row.append(row[gpose_para_header[0]])  # para name
        sim_parameters_row.append(row[gpose_para_header[1]])  # units
        key = str(row[gpose_para_header[2]]).strip()
        sim_parameters_row.append(key)  # key
        para_val = float(request.GET.get(key, row[gpose_para_header[3]]))
        if key == 'del_time' and para_val > 1.0: # prevent user entering del_time > 1.0
            para_val = 0.1
        sim_parameters_row.append(para_val)  # para value
        sim_parameters_dict[key] = para_val
        sim_parameters.append(sim_parameters_row)

    x_min = request.GET.get('x_min',0)
    x_max = request.GET.get('x_max',0)
    y_min = request.GET.get('y_min',0)
    y_max = request.GET.get('y_max',0)
    x_log = request.GET.get('x_log', 'False')
    y_log = request.GET.get('y_log', 'False')
    scale = request.GET.get('scale', '1.0')

    c_label = request.GET.get('c_label', "False")

    if c_label == "True":
        x_label = request.GET.get('x_label', 'Time (sec)')
        y_label = request.GET.get('y_label', "Count Rate (counts/sec)")
        title = request.GET.get('title', 'GPOSE Light Curves')

    else:
        x_label = request.GET.get('x_label', 'Time (sec)')
        y_label = request.GET.get('y_label', "Count Rate (counts/sec)")
        if scale != 1.0:
            y_label = "Count Rate (" + str(scale) + " counts/sec)"
        title = request.GET.get('title', 'GPOSE Light Curves')

    gpose_radius = sim_parameters_dict['gpose_radius']
    num_telescope = sim_parameters_dict['num_telescope']
    num_channels = sim_parameters_dict['num_channels']
    gpose_fov = gpose.get_fov(gpose_radius)
    gpose_fov_deg = gpose_fov * (180.0 / math.pi)**2.0
    telescope_fov = gpose_fov/num_telescope
    telescope_fov_deg = telescope_fov * (180.0 / math.pi)**2.0
    telescope_fov_radius = gpose.get_fov_radius(telescope_fov)
    channel_fov = telescope_fov/num_channels
    channel_fov_deg = channel_fov * (180.0 / math.pi)**2.0
    channel_fov_radius = gpose.get_fov_radius(channel_fov)

    # for 16 channel camera
    h = 12.0  # mm
    focal_length_16 = h/np.tan(telescope_fov_radius/180.0*np.pi)/2.0

    # for 64 channel camera
    h = 24.0  # mm
    focal_length_64 = h/np.tan(telescope_fov_radius/180.0*np.pi)/2.0

    sky_background = sim_parameters_dict['sky_background']
    k_V = sim_parameters_dict['k_V']
    alpha = sim_parameters_dict['alpha']
    zmoon = sim_parameters_dict['zmoon']
    z = sim_parameters_dict['z']
    rho = sim_parameters_dict['rho']

    # correction for the correct angular distance to the moon
    if np.abs(zmoon-z) > rho:
        rho = np.abs(zmoon-z)
        sim_parameters_dict['rho'] = rho
        for simp in sim_parameters:
            if simp[2] == 'rho':
                simp[3] = rho

    bMoon, deltaV = gpose_sky.moonSkyMag(alpha, rho, z, zmoon, k_V, sky_background)
    bMoonMag = gpose_sky.nanoLambertToMag(bMoon)

    sim_results = []
    sim_results_row = ['GPOSE Observatory FOV', 'square degrees', "%.2f" % gpose_fov_deg]
    sim_results.append(sim_results_row)
    sim_results_row = ['GPOSE Observatory FOV', 'steradian', "%.2f" % gpose_fov]
    sim_results.append(sim_results_row)
    sim_results_row = ['Telescope FOV Radius', 'degrees', "%.2f" % telescope_fov_radius]
    sim_results.append(sim_results_row)
    sim_results_row = ['Telescope FOV', 'square degrees', "%.2f" % telescope_fov_deg]
    sim_results.append(sim_results_row)
    sim_results_row = ['Telescope FOV', 'steradian', "%.3f" % telescope_fov]
    sim_results.append(sim_results_row)
    sim_results_row = ['Channel FOV Radius', 'degrees', "%.2f" % channel_fov_radius]
    sim_results.append(sim_results_row)
    sim_results_row = ['Channel FOV', 'square degrees', "%.2f" % channel_fov_deg]
    sim_results.append(sim_results_row)
    sim_results_row = ['Channel FOV', 'steradian', "%.5f" % channel_fov]
    sim_results.append(sim_results_row)

    sim_results_row = ['Brightness due to Moon at the Sky Location (V)', 'Mag', "%.5f" % bMoonMag]
    sim_results.append(sim_results_row)
    sim_results_row = ['Change in Sky Background due to Moon (V)', 'Mag', "%.5f" % deltaV]
    sim_results.append(sim_results_row)
    sim_results_row = ['Focal length of the objective lense (16 Channel) ', 'mm', "%.1f" % focal_length_16]
    sim_results.append(sim_results_row)
    sim_results_row = ['Focal length of the objective lense (64 Channel) ', 'mm', "%.1f" % focal_length_64]
    sim_results.append(sim_results_row)

    #import ipdb; ipdb.set_trace() # debugging code

    return render_to_response('gpose_sim_page.html', {'sim_parameters': sim_parameters,
                                                     'sim_results': sim_results,
                                                     'x_label': x_label,
                                                     'y_label': y_label,
                                                     'title': title,
                                                     'c_label': c_label,
                                                     'scale': scale,
                                                     'x_min': x_min,
                                                     'x_max': x_max,
                                                     'y_min': y_min,
                                                     'y_max': y_max,
                                                     'x_log': x_log,
                                                     'y_log': y_log,
    })

#@login_required(login_url=login_url)
def gpose_sim_plot(request):

    fig = Figure(figsize=(12, 7), edgecolor='white', facecolor='white')
    fig.subplots_adjust(top=0.95)
    fig.subplots_adjust(bottom=0.07)
    fig.subplots_adjust(left=0.06)
    fig.subplots_adjust(right=0.98)

    plot_type = request.GET.get('plot_type', 'png')

    gpose_para_df = pandas.read_csv(gpose_sim_parameters)
    gpose_para_header = gpose_para_df.columns
    sim_parameters = {}

    for index, row in gpose_para_df.iterrows():
        #print row[key_map_header[0]], row[key_map_header[1]], row[key_map_header[2]]
        key = str(row[gpose_para_header[2]]).strip()
        para_val = float(request.GET.get(key, row[gpose_para_header[3]]))
        sim_parameters[key] = para_val

    x_log = request.GET.get('x_log', 'False')
    y_log = request.GET.get('y_log', 'False')
    scale = float(request.GET.get('scale', '1.0'))

    x_label = request.GET.get('x_label', 'Time (sec)')
    y_label = request.GET.get('y_label', "Count Rate (" + str(scale) + " counts/sec)")
    title = request.GET.get('title', 'GPOSE Light Curves')

    #import pdb; pdb.set_trace() # debugging code

    """
    if x_log == 'True':
        if len(unit1) > 1:
            if unit1 != 'None':
                x_label = 'log ' + request.GET.get('x_label', type_id_01) + ' (' + unit1 + ')'
            else:
                x_label = 'log ' + request.GET.get('x_label', type_id_01)
        else:
            x_label = 'log ' + request.GET.get('x_label', type_id_01)

    else:
        if len(unit1) > 1:
            if unit1 != 'None':
                x_label = request.GET.get('x_label', type_id_01) + ' (' + unit1 + ')'
            else:
                x_label = request.GET.get('x_label', type_id_01)
        else:
            x_label = request.GET.get('x_label', type_id_01)

    if y_log == 'True':
        if len(unit2) > 1:
            if unit2 != 'None':
                y_label = 'log ' + request.GET.get('y_label', type_id_02) + ' (' + unit2 + ')'
            else:
                y_label = 'log ' + request.GET.get('y_label', type_id_02)
        else:
            y_label = 'log ' + request.GET.get('y_label', type_id_02)

    else:
        if len(unit2) > 1:
            if unit2 != 'None':
                y_label = request.GET.get('y_label', type_id_02) + ' (' + unit2 + ')'
            else:
                y_label = request.GET.get('y_label', type_id_02)
        else:
            y_label = request.GET.get('y_label', type_id_02)
    """

    ra = float(sim_parameters['ra'])
    dec = float(sim_parameters['dec'])
    sky_background = float(sim_parameters['sky_background'])
    k_V = float(sim_parameters['k_V'])
    alpha = float(sim_parameters['alpha'])
    zmoon = float(sim_parameters['zmoon'])
    z = float(sim_parameters['z'])
    rho = float(sim_parameters['rho'])

    bMoon, deltaV = gpose_sky.moonSkyMag(alpha, rho, z, zmoon, k_V, sky_background)
    sky_background = sky_background + deltaV  # add the contribution from the moon to the sky background

    gpose_radius = float(sim_parameters['gpose_radius'])
    num_telescope = float(sim_parameters['num_telescope'])
    num_channels = float(sim_parameters['num_channels'])
    telescope_radius = float(sim_parameters['telescope_radius'])
    gap_efficiency = float(sim_parameters['gap_efficiency'])
    profile = float(sim_parameters['profile'])
    t90 = float(sim_parameters['t90'])
    del_time = float(sim_parameters['del_time'])
    telescope_fov = gpose.get_fov(gpose_radius)/num_telescope
    channel_fov = telescope_fov/num_channels
    channel_fov_radius = gpose.get_fov_radius(channel_fov)

    time1, rate1, rateErr1 = gpose.create_gpose_lightcurve(sim_parameters['grb_mag1'],
                                                           sky_background,
                                                           ra,
                                                           dec,
                                                           channel_fov_radius,
                                                           telescope_radius,
                                                           gap_efficiency,
                                                           profile,
                                                           del_time,
                                                           t90=t90)

    time2, rate2, rateErr2 = gpose.create_gpose_lightcurve(sim_parameters['grb_mag2'],
                                                           sky_background,
                                                           ra,
                                                           dec,
                                                           channel_fov_radius,
                                                           telescope_radius,
                                                           gap_efficiency,
                                                           profile,
                                                           del_time,
                                                           t90=t90)

    time3, rate3, rateErr3 = gpose.create_gpose_lightcurve(sim_parameters['grb_mag3'],
                                                           sky_background,
                                                           ra,
                                                           dec,
                                                           channel_fov_radius,
                                                           telescope_radius,
                                                           gap_efficiency,
                                                           profile,
                                                           del_time,
                                                           t90=t90)

    time4, rate4, rateErr4 = gpose.create_gpose_lightcurve(sim_parameters['grb_mag4'],
                                                           sky_background,
                                                           ra,
                                                           dec,
                                                           channel_fov_radius,
                                                           telescope_radius,
                                                           gap_efficiency,
                                                           profile,
                                                           del_time,
                                                           t90=t90)

    title = request.GET.get('title', 'GPOSE Light Curve')

    ax = fig.add_subplot(111)

    plot_line_color = ['k', 'g', 'r', 'b', 'm', 'y', 'c']

    #y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
    #ax.yaxis.set_major_formatter(y_formatter)

    ax.plot(time1, rate1/scale, color=plot_line_color[0], linestyle='steps', label="GRB 01 (Mag: " + str(sim_parameters['grb_mag1']) + ")")
    ax.plot(time2, rate2/scale, color=plot_line_color[1], linestyle='steps', label="GRB 02 (Mag: " + str(sim_parameters['grb_mag2']) + ")")
    ax.plot(time3, rate3/scale, color=plot_line_color[2], linestyle='steps', label="GRB 03 (Mag: " + str(sim_parameters['grb_mag3']) + ")")
    ax.plot(time4, rate4/scale, color=plot_line_color[3], linestyle='steps', label="GRB 04 (Mag: " + str(sim_parameters['grb_mag4']) + ")")

    #ax.errorbar(time4, rate4, yerr=rateErr4, fmt='o')

    #for k in range(len(x_arr)):
    #    ax.plot(x_arr[k], y_arr[k]*1.0e-6, color=plot_line_color[k], linestyle='steps', label=label_arr[k])

    ax.legend(loc=0)
    #import ipdb; ipdb.set_trace() # debugging code

    x_scale_min = float(request.GET.get('x_min', 0))
    x_scale_max = float(request.GET.get('x_max', 0))
    y_scale_min = float(request.GET.get('y_min', 0))
    y_scale_max = float(request.GET.get('y_max', 0))

    if (x_scale_min < x_scale_max) and (y_scale_min < y_scale_max):
        #import pdb; pdb.set_trace() # debugging code
        ax.axis([x_scale_min, x_scale_max, y_scale_min, y_scale_max])


    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    fig.tight_layout()

    canvas = FigureCanvas(fig)

    if plot_type == 'png':
        response=HttpResponse(content_type='image/png')
        canvas.print_png(response)

    if plot_type == 'pdf':
        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="light_curve.pdf"'
        #response=django.http.HttpResponse(content_type='image/pdf')
        #response=['Content-Disposition'] = 'attachment; filename=plot.pdf'
        #canvas.Canvas(response)
        canvas = PdfFigureCanvas(fig)
        canvas.print_pdf(response)

    """
    if plot_type == 'text':
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename="light_curve.csv"'
        writer = csv.writer(response)
        num_points = len(x)
        if num_points > 0:
            writer.writerow(['X Values'])
            for i in range(num_points):
                writer.writerow([x[i]])
            writer.writerow(['Y Values'])
            for i in range(num_points):
                writer.writerow([y[i]])
        else:
            writer.writerow(["No data!"])
    """

    return response


# This is an example code
def plot(request):

    fig = Figure(figsize=(14, 8), edgecolor='white', facecolor='white')
    fig.subplots_adjust(top=0.99)
    fig.subplots_adjust(bottom=0.05)
    fig.subplots_adjust(left=0.05)
    fig.subplots_adjust(right=0.99)

    import numpy as np
    x = np.random.randn(100)
    y = np.random.randn(100)

    xlabel = "x"
    ylabel = "Y"

    x_min = -3
    x_max = 3
    y_min = -3
    y_max = 3

    title = "Test Plot"

    ax=fig.add_subplot(111)
    ax.plot(x, y, 'r', linewidth=2.0)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.text(0.05, 0.9, title,
        fontsize=20,
        bbox={'facecolor':'white'},
        horizontalalignment='left',
        verticalalignment='center',
        transform = ax.transAxes)
    ax.axis([x_min, x_max, y_min, y_max])

    canvas=FigureCanvas(fig)
    response=HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response


