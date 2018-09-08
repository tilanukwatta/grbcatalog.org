#!/usr/bin/env python

# source http://www.batse.msfc.nasa.gov/batse/grb/catalog/current/

#  >>python manage.py shell
#  >>execfile('insert_batse_data.py') 

# http://swift.gsfc.nasa.gov/archive/grb_table/grb_table.php?obs=Swift&year=All+Years&restrict=none&grb_time=1&grb_trigger=1&burst_advocate=1&other_obs=1&redshift=1&host=1&comments=1&references=1&bat_ra=1&bat_dec=1&bat_err_radius=1&bat_t90=1&bat_fluence=1&bat_err_fluence=1&bat_1s_peak_flux=1&bat_err_1s_peak_flux=1&bat_photon_index=1&bat_err_photon_index=1&xrt_ra=1&xrt_dec=1&xrt_err_radius=1&xrt_first_obs=1&xrt_early_flux=1&xrt_11hr_flux=1&xrt_24hr_flux=1&xrt_lc_index=1&xrt_gamma=1&xrt_nh=1&uvot_ra=1&uvot_dec=1&uvot_err_radius=1&uvot_first_obs=1&uvot_vmag=1&uvot_filters=1&view.x=20&view.y=16&view=submit
# http://swift.gsfc.nasa.gov/archive/grb_table/fullview/

# use django 1.5

from django.core.management import setup_environ
import settings
setup_environ(settings)

#import os
#import django

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grbcatalog.settings")
#django.setup()

#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
#from django.conf import settings

from django.core.exceptions import ObjectDoesNotExist

import csv
from grb.models import grb, observatory, grb_observatory_list, measurement, measurement_type, grb_type, grb_type_list, reference
#from grbcatalog.datelib import julian_day
from django.contrib.auth.models import User
from datetime import date
from datetime import datetime
from django.utils.timezone import utc

#import operator

#import ipdb; ipdb.set_trace() # debugging code

def insert_grb_measurement(row):
    grb_name = row[0]
    grb_mea_type = row[1]
    units = row[3]
    data_type = row[6]
    unitstex = units
    comments = ""
    if data_type == "FLOAT":
        if grb_mea_type == 'Redshift':
            comments = str(row[2]).strip()
            redshiftStr = comments.split()[0]
            if (redshiftStr.find('<') >=0) or (redshiftStr.find('~') >=0):
                value = 0
            else:
                value = float(redshiftStr)
        else:
            valueStr = str(row[2]).strip()
            if (valueStr.find('<') >= 0) or (valueStr.find('>') >= 0) or (valueStr.find('~') >= 0):
                value = float(valueStr[1:])
                comments = valueStr
            else:
                if (valueStr.find('|') >= 0):
                    value = float(valueStr.split('|')[0])
                    comments = valueStr
                else:
                    value = float(valueStr)
    else:
        value = 0

    value_error1Str = str(row[4]).strip()
    if value_error1Str.find('~') >= 0:
        value_error1 = float(value_error1Str[1:])
    else:
        if value_error1Str.find('n/a') >= 0:
            value_error1 = float(0)
        else:
            value_error1 = float(value_error1Str)

    value_error2Str = str(row[5]).strip()
    if value_error2Str.find('~') >= 0:
        value_error2 = float(value_error2Str[1:])
    else:
        if value_error2Str.find('n/a') >= 0:
            value_error2 = float(0)
        else:
            value_error2 = float(value_error2Str)

    if data_type == "DATE":
        mdate = row[2]
    else:
        mdate = grb_datetime.replace(year=int(1000),
                                     month=1,
                                     day=1,
                                     hour=0,
                                     minute=0,
                                     second=0,
                                     microsecond=0,
                                     tzinfo=utc)

    if data_type == "TEXT":
        comments = str(row[2]).strip()
        #redshiftStr = comments.split()[0]
        #if grb_mea_type == 'Redshift':
        #    if (redshiftStr.find('<') >=0) or (redshiftStr.find('~') >=0):
        #        pass
        #    else:
        #        value = float(redshiftStr)
            #print grb_name, ' : ', grb_mea_type, " = " , comments, redshiftStr, ' Value: ', value
        #import pdb; pdb.set_trace() # debugging code

    try:
        grb_dbitem = grb.objects.get(grb_name=grb_name)
    except ObjectDoesNotExist:
        print "GRB " + str(grb_name) + " does not exist. Inserting a new GRB record..."
        grb_dbitem = grb(grb_name=grb_name,
            entry_person=entry_name
        )
        grb_dbitem.save()
        insert_grb_measurement(row)

    try:
        grb_mea_item = measurement_type.objects.get(measurement_type_name=grb_mea_type)
    except ObjectDoesNotExist:
        print "Measurement Type does not exist. Inserting a new measurement type..."
        grb_mea_item = measurement_type(measurement_type_name=grb_mea_type,
            data_type=data_type,
            units=units,
            units_latex=unitstex,
            reference=reference.objects.get(title='Swift BAT Catalog'),
            entry_person=entry_name,
            comments=" "
        )
        grb_mea_item.save()
        insert_grb_measurement(row)

    try:
        grb_measurement = measurement.objects.get(grb_name=grb_dbitem, measurement_type=grb_mea_item)
        print "GRB ", grb_dbitem.grb_name, " measurement exist..."
    except ObjectDoesNotExist:
        print "GRB Measurement does not exist. Inserting a new measurement..."
        print grb_dbitem.grb_name, grb_mea_item.measurement_type_name, value, value_error1, value_error2, comments, mdate
        grb_measurement = measurement(grb_name=grb_dbitem,
            measurement_type=grb_mea_item,
            value=value,
            value_error_positive=value_error1,
            value_error_negative=value_error2,
            text = comments,
            date = mdate,
            reference=reference.objects.get(title='Swift BAT Catalog'),
            entry_person=entry_name
            )
        #import pdb; pdb.set_trace() # debugging code
        grb_measurement.save()

def insert_reference():
    try:
        grb_ref = reference.objects.get(title='Swift BAT Catalog')
        print "GRB Reference exist..."
    except ObjectDoesNotExist:
        print "GRB Reference does not exist. Inserting a new reference..."
        #insert the reference information
        ref_date = date.today()
        ref_item = reference(title='Swift BAT Catalog',
            authors='Swift Team',
            date=ref_date.replace(year=2012, month=11, day=1),
            journal=' ',
            volume=' ',
            pages=' ',
            url='http://swift.gsfc.nasa.gov/docs/swift/archive/grb_table/',
            entry_person=entry_name,
            comments='Taken from Swift Website'
        )
        ref_item.save()

def get_ra_coordinates(coor):
    coordinates = str(coor).split(":")
    hour = 360.0/24.0
    minute = 360.0/24.0/60.0
    sec = 360.0/24.0/60.0/60.0
    return hour*float(coordinates[0]) + minute*float(coordinates[1]) + sec*float(coordinates[2])

def get_dec_coordinates(coor):
    coordinates = str(coor).split(":")
    minute = 1.0/60.0
    sec = 1.0/60.0/60.0
    if float(coordinates[0]) > 0:
        return float(coordinates[0]) + minute*float(coordinates[1]) + sec*float(coordinates[2])
    else:
        return float(coordinates[0]) - minute*float(coordinates[1]) - sec*float(coordinates[2])

if __name__ == '__main__':
    #print get_ra_coordinates('23:15:47.5')
    #print get_dec_coordinates('-44:38:42.3')
    #import pdb; pdb.set_trace() # debugging code

    
    entry_name = User.objects.get(username='tilan')
    csv.register_dialect('grbcatalog', delimiter='\t', quoting=csv.QUOTE_NONE, skipinitialspace=True)
    swift_grbs = csv.reader(open('data/swift/grb_table_total_no_header.txt', 'rb'), 'grbcatalog')

    #import ipdb; ipdb.set_trace() # debugging code

    data_swift = []
    data_swift.extend(swift_grbs) # put items in into a array
    row_num = len(data_swift)
    header = data_swift[0]
    col_num = len(header)

    #import ipdb; ipdb.set_trace() # debugging code

    measurement_name = []
    measurement_unit = []
    for j in range(0, col_num, 1):
        meas_name = str(header[j]).replace("<br>", " ")
        index1 = meas_name.find('[')
        index2 = meas_name.find(']')
        if index1 > 0:
            units = meas_name[index1+1:index2]
            name = meas_name[:index1].strip()
        else:
            units = "None"
            name = meas_name
        measurement_name.append(name)
        measurement_unit.append(units)
        print j, ' Name: ', name, 'Units: ', units

    #import ipdb; ipdb.set_trace() # debugging code

    # unpack text file and load GRB data into a list
    measurement_value = []

    for i in range(1, row_num, 1):
        m_values = []
        grb_item = list(data_swift[i])
        col_num = len(grb_item)
        if col_num < 35:
            grb_item.append("")
            grb_item.append("")
        col_num = len(grb_item)
        if col_num < 35:
            grb_item.append("")
            grb_item.append("")
            grb_item.append("")
            grb_item.append("")
            #print grb_item, col_num
        col_num = len(grb_item)
        if col_num < 35:
            print grb_item, col_num
        #print grb_item, col_num

        grb_name = grb_item[0]
        if len(grb_name) == 6:
            grb_name = grb_name + 'A'

        grb_time = grb_item[1]
        if len(grb_time)< 8:
            grb_time='00:00:00'

        grb_datetime = datetime.utcnow()

        #if grb_name[0:2] == '+1':
        #    import pdb; pdb.set_trace() # debugging code

        grb_datetime = grb_datetime.replace(year=int('20' + grb_name[0:2]),
                                            month=int(grb_name[2:4]),
                                            day=int(grb_name[4:6]),
                                            hour=int(grb_time[0:2]),
                                            minute=int(grb_time[3:5]),
                                            second=int(grb_time[6:8]),
                                            microsecond=0,
                                            tzinfo=utc)

        trigger_num = grb_item[2]
        bat_ra =  grb_item[3]
        bat_dec =  grb_item[4]
        bat_90_error_radius = grb_item[5]
        bat_t90 = grb_item[6]
        bat_fluence = grb_item[7]
        bat_fluence_error = grb_item[8]
        bat_peak_ph_flux = grb_item[9]
        bat_peak_ph_flux_error = grb_item[10]
        bat_ph_index = grb_item[11]
        bat_ph_index_error = grb_item[12]
        #import pdb; pdb.set_trace() # debugging code
        print grb_name, grb_datetime, trigger_num, bat_ra, bat_dec, bat_90_error_radius, bat_t90, bat_fluence, bat_fluence_error, \
              bat_peak_ph_flux, bat_peak_ph_flux_error, bat_ph_index, bat_ph_index_error

        m_values.append(grb_name)
        m_values.append(grb_datetime)
        m_values.append(trigger_num)
        m_values.append(bat_ra)
        m_values.append(bat_dec)
        m_values.append(bat_90_error_radius)
        m_values.append(bat_t90)
        m_values.append(bat_fluence)
        m_values.append(bat_fluence_error)
        m_values.append(bat_peak_ph_flux)
        m_values.append(bat_peak_ph_flux_error)
        m_values.append(bat_ph_index)
        m_values.append(bat_ph_index_error)

        xrt_ra =  grb_item[13]
        xrt_dec =  grb_item[14]
        xrt_90_error_radius = grb_item[15]
        xrt_time_to_first_obs = grb_item[16]
        xrt_early_flux = grb_item[17]
        xrt_11_hour_flux = grb_item[18]
        xrt_24_hour_flux = grb_item[19]
        xrt_inital_temporal_index = grb_item[20]
        xrt_spectral_index = grb_item[21]
        xrt_column_density = grb_item[22]

        print grb_name, xrt_ra, xrt_dec, xrt_90_error_radius, xrt_time_to_first_obs, xrt_early_flux, xrt_11_hour_flux, xrt_24_hour_flux, \
              xrt_inital_temporal_index, xrt_spectral_index, xrt_column_density
        m_values.append(xrt_ra)
        m_values.append(xrt_dec)
        m_values.append(xrt_90_error_radius)
        m_values.append(xrt_time_to_first_obs)
        m_values.append(xrt_early_flux)
        m_values.append(xrt_11_hour_flux)
        m_values.append(xrt_24_hour_flux)
        m_values.append(xrt_inital_temporal_index)
        m_values.append(xrt_spectral_index)
        m_values.append(xrt_column_density)

        uvot_ra =  grb_item[23]
        uvot_dec =  grb_item[24]
        uvot_90_error_radius = grb_item[25]
        uvot_time_to_first_obs = grb_item[26]
        uvot_magnitude = grb_item[27]
        uvot_other_filter_magnitude = grb_item[28]

        print grb_name, uvot_ra, uvot_dec, uvot_90_error_radius, uvot_time_to_first_obs, uvot_magnitude, uvot_other_filter_magnitude
        m_values.append(uvot_ra)
        m_values.append(uvot_dec)
        m_values.append(uvot_90_error_radius)
        m_values.append(uvot_time_to_first_obs)
        m_values.append(uvot_magnitude)
        m_values.append(uvot_other_filter_magnitude)

        other_observatory_detections = grb_item[29]
        redshift = grb_item[30]
        hostgalaxy = grb_item[31]
        comments = grb_item[32]
        references = grb_item[33]
        ba = grb_item[34]

        print grb_name, other_observatory_detections, redshift, hostgalaxy, comments, references, ba
        m_values.append(other_observatory_detections)
        m_values.append(redshift)
        m_values.append(hostgalaxy)
        m_values.append(comments)
        m_values.append(references)
        m_values.append(ba)

        measurement_value.append(m_values)

    for grb_row in measurement_value:
        print grb_row

    #import ipdb; ipdb.set_trace() # debugging code

    # create a list of rows to be inserted to the data base
    data_row_list = []
    for j in range(0, row_num-1, 1): # need to subtract one since header does not count (go through GRBs in the list)
        #print ''
        for i in range(1, col_num, 1): # skip the GRB name col (go through GRBs measurements in the list)
            data_row = []
            data_type = "FLOAT"
            print i, j

            if (i == 8) or (i == 10) or (i == 12) or (str(measurement_value[j][i]).find('n/a') >= 0)or (str(measurement_value[j][i]).find('TBD') >= 0) or (str(measurement_value[j][i]) == ""):
                pass
            else:
                data_row.append(measurement_value[j][0])
                if (i == 7) or (i == 9) or (i == 11):
                    if i == 11:
                        if str(measurement_value[j][i]).find("CPL")>0:
                            data_row.append('BAT Photon Index (15-150 keV) (CPL = cutoff power-law)')
                        else:
                            data_row.append('BAT Photon Index (15-150 keV) (PL = simple power-law)')
                        data_row.append(str(measurement_value[j][i]).split(',')[0])
                        errorStr = str(measurement_value[j][12])
                        if (errorStr.find("/") > 0) and (errorStr.find("n/a") < 0):
                            error1 = float(errorStr.split("/")[0])
                            error2 = float(errorStr.split("/")[1])
                            data_row.append(measurement_unit[i])
                            if error1 > error2:
                                data_row.append(errorStr.split("/")[1])
                                data_row.append(errorStr.split("/")[0])
                            else:
                                data_row.append(errorStr.split("/")[0])
                                data_row.append(errorStr.split("/")[1])
                            #
                        else:
                            data_row.append(measurement_unit[i])
                            data_row.append(errorStr)
                            data_row.append(errorStr)
                    if i == 9:
                        data_row.append(measurement_name[i])
                        data_row.append(measurement_value[j][i])
                        errorStr = str(measurement_value[j][10])
                        data_row.append(measurement_unit[i])
                        if errorStr.find("/") > 0:
                            #import pdb; pdb.set_trace() # debugging code
                            data_row.append(0)
                            data_row.append(0)
                        else:
                            data_row.append(errorStr)
                            data_row.append(errorStr)
                    if i == 7:
                        data_row.append(measurement_name[i])
                        data_row.append(measurement_value[j][i])
                        errorStr = str(measurement_value[j][8])
                        data_row.append(measurement_unit[i])
                        if errorStr.find("/") > 0:
                            #import pdb; pdb.set_trace() # debugging code
                            data_row.append(0)
                            data_row.append(0)
                        else:
                            data_row.append(errorStr)
                            data_row.append(errorStr)
                else:
                    if i == 1:
                        data_type = "DATE"
                    if (i == 32) or (i == 29) or (i == 2) or (i == 27) or (i == 28) or (i == 34) or (i == 31):
                        data_type = "TEXT"
                    data_row.append(measurement_name[i])

                    if (i == 13) or (i == 23):
                        data_row.append(get_ra_coordinates(measurement_value[j][i]))
                        data_row.append("deg")
                    else:
                        if (i == 14) or (i == 24):
                            data_row.append(get_dec_coordinates(measurement_value[j][i]))
                            data_row.append("deg")
                        else:
                            if (i == 3) or (i == 4):
                                if (i == 3) and (str(measurement_value[j][i]).find(':') >= 0):
                                    data_row.append(get_ra_coordinates(measurement_value[j][i]))
                                else:
                                    if (i == 4) and (str(measurement_value[j][i]).find(':') >= 0):
                                        data_row.append(get_dec_coordinates(measurement_value[j][i]))
                                    else:
                                        data_row.append(measurement_value[j][i])

                                data_row.append("deg")
                            else:
                                data_row.append(measurement_value[j][i])
                                data_row.append(measurement_unit[i])
                    data_row.append(0)
                    data_row.append(0)
                data_row.append(data_type)
                print data_row
                data_row_list.append(data_row)
            #import pdb; pdb.set_trace() # debugging code
            #print i, j, measurement_name[i], ' = ', measurement_value[j][i], '(', measurement_unit[i], ')'
            #row = [measurement_name[i], measurement_value[j][i], measurement_unit[i]]
            #print row

    for item in data_row_list:
        print item

    # a check
    for item in data_row_list:
        if len(item) != 7:
            print item, len(item)
            import ipdb; ipdb.set_trace() # debugging code
    print "No issues"

    #import ipdb; ipdb.set_trace() # debugging code

    insert_reference()
    #stop = 1500
    #index = 0
    for item in data_row_list:
        grb_name = item[0]
        print grb_name, item, len(item)
        insert_grb_measurement(item)
        #index += 1
        #import pdb; pdb.set_trace() # debugging code

