#!/usr/bin/env python

# http://en.wikipedia.org/wiki/Julian_day

import time
from datetime import datetime
from django.utils.timezone import utc

def get_jd(year, mon, day, hour, min, sec):
    a = (14-mon)/12
    y = year+4800-a
    m = mon+12*a-3

    JDN = day + (153*m+2)/5 + 365*y + y/4 - y/100 + y/400 - 32045
    JD = JDN + (hour-12)/24.0 + min/1440.0 + sec/86400.0
    return JD
    
def get_mjd(year, mon, day, hour, min, sec):
    return get_jd(year, mon, day, hour, min, sec) - 2400000.5

def get_today_in_jd():
    today = time.localtime()

    year = today[0]
    mon  = today[1]
    day  = today[2]
    hour = today[3]
    min  = today[4]
    sec  = today[5]

    return get_jd(year, mon, day, hour, min, sec)

def get_today_in_mjd():
    return get_today_in_jd() - 2400000.5

#print get_today_in_mjd()

#JD = JDN + (hour-12)/24.0 + min/1440.0 + sec/86400.0

def get_gregorian_date_from_jd(jd):
    j = int(jd + 0.5) + 32044
    g = j/146097
    dg = j%146097
    c = ((dg/36524+1)*3)/4
    dc = dg - c * 36524
    b = dc/1461
    db = dc%1461
    a = (db/365+1)*3/4
    da = db-a*365
    y = g*400 + c*100 + b*4 + a
    m = (da*5+308)/153-2
    d = da-(m+4)*153/5+122
    
    yy = y-4800+(m+2)/12
    mm = (m+2)%12+1
    dd = d + 1
   
    j = jd + 0.5
    timefrac = j - int(j)
    time_h = timefrac * 24
    hour = int(time_h)
    time_m = timefrac * 1440
    min = int(time_m - hour*60)
    time_s = timefrac * 86400
    sec = abs(int(time_s - hour*60*60 - min*60))
           
    #date = [yy, mm, dd, hour, min, sec]
    
    return datetime(yy, mm, dd, hour, min, sec, 0, tzinfo=utc)

def get_gregorian_date_from_mjd(mjd):
    jd = mjd + 2400000.5
    return get_gregorian_date_from_jd(jd)

#print time.localtime()
#mjd = get_today_in_mjd()
#print mjd
#print get_gregorian_date_from_mjd(mjd)



