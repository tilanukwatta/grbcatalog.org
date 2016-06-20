import numpy as np
from scipy.optimize import curve_fit
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import math
#from scipy.integrate import quad # integration library
#import datetime
#import time
#import csv
#import os
from scipy.interpolate import interp1d
import grbcatalog.secrets as secrets
import pandas

if secrets.site == 'local':
    star_catalog = '/home/tilan/Desktop/Dropbox/django/grbcatalog/grbcatalog/gpose/star_catalog.dat'
    star_photon_counts = '/home/tilan/Desktop/Dropbox/django/grbcatalog/grbcatalog/gpose/star_photon_counts.dat'
else:
    star_catalog = '/web_app/grbcatalog/grbcatalog/gpose/star_catalog.dat'
    star_photon_counts = '/web_app/grbcatalog/grbcatalog/gpose/star_photon_counts.dat'

#sky_background = 21.5 # mag/arcsec^2 in V (551 nm)
#telescope_fov = 0.85
efficiency = 0.4

zero_point_flux_V = 3600 # Jy
zero_point_flux_R = 3060 # Jy
JytoW = 1.0e-26 # W m^-2 Hz^-1
V = 551.0  # nm
deltaV = 88.0 # nm
R = 658.0  # nm
deltaR = 138.0 # nm
c = 2.9979e8 # m/s
h = 6.626e-34 # Js
arcMinToDeg = 1.0/60.0
arcSecToDeg = 1.0/60.0/60.0
nm2m = 1.0e-9
inch2m = 0.0254

def get_fov(theta):
    # Return the solid angle of a cone with apex angle 2 theta, is the area of a spherical cap on a unit sphere.
    theta_rad = theta * math.pi / 180.0
    return 2.0 * math.pi * (1.0 - math.cos(theta_rad))

def get_fov_deg(theta):
    fov_deg = get_fov(theta)
    return fov_deg * (180.0 / math.pi)**2.0

def get_fov_radius(fov):
    radius = np.arccos(1.0 - (fov/(2.0 * math.pi)))
    radius_deg = radius * 180.0 / math.pi
    return radius_deg

def get_frequency(wavelenght):
    return np.float(c/wavelenght)

def get_energy(wavelenght):
    return get_frequency(wavelenght) * h  # J

def get_frequency_width(L, deltaL):
    f1 = np.float(c/((L-deltaL)*nm2m))
    f2 = np.float(c/((L+deltaL)*nm2m))
    return f1 - f2

def get_photon_rate_from_mag_v(mag=0):
    flux_per_Hz = 10.0**(-mag/2.5) * zero_point_flux_V * JytoW  # W m^-2 Hz^-1
    flux = flux_per_Hz * get_frequency_width(V, deltaV)  # W m^-2 (J/s/m^2)
    #flux = flux_per_Hz * get_frequency(V * nm2m)  # W m^-2 (J/s/m^2)
    count_rate = flux/get_energy(V * nm2m)  # ph/s/m^2
    return count_rate

def get_photon_rate_from_mag_r(mag=0):
    flux_per_Hz = 10.0**(-mag/2.5) * zero_point_flux_R * JytoW  # W m^-2 Hz^-1
    flux = flux_per_Hz * get_frequency_width(R, deltaR)  # W m^-2 (J/s/m^2)
    #flux = flux_per_Hz * get_frequency(R * nm2m)  # W m^-2 (J/s/m^2)
    count_rate = flux/get_energy(R * nm2m)  # ph/s/m^2
    return count_rate

def plot_lightcurve(x, y, yErr, title, xlabel, ylabel, plot_name):
    plt.subplots_adjust(hspace=0.4)
    ax = plt.subplot(111)

    ax.errorbar(x, y, yerr=yErr, fmt='o', color='b')
    ax.plot(x, y, 'k')
    #ax.axhline(linewidth=axis_width, color="k")
    #ax.axvline(linewidth=axis_width, color="k")

    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.savefig(plot_name)
    plt.clf()

def plot_lightcurve_bar(x, y, yErr, title, xlabel, ylabel, plot_name):
    plt.subplots_adjust(hspace=0.4)
    ax = plt.subplot(111)

    ax.plot(x, y, color='b', linestyle='steps')
    #ax.plot(x, y, 'k')
    #ax.axhline(linewidth=axis_width, color="k")
    #ax.axvline(linewidth=axis_width, color="k")

    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.savefig(plot_name)
    plt.clf()

def plot_lightcurve_bar_array(x_arr, y_arr, label_arr, title, xlabel, ylabel, plot_name):

    plt.subplots_adjust(hspace=0.4)
    ax = plt.subplot(111)
    num = len(x_arr)
    plot_line_color = ['k', 'g', 'r', 'b', 'm', 'y', 'c',]

    y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
    ax.yaxis.set_major_formatter(y_formatter)

    for k in range(num):
        ax.plot(x_arr[k], y_arr[k]*1.0e-6, color=plot_line_color[k], linestyle='steps', label=label_arr[k])

    ax.legend(loc=0)
    #ax.plot(x, y, 'k')
    #ax.axhline(linewidth=axis_width, color="k")
    #ax.axvline(linewidth=axis_width, color="k")

    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.savefig(plot_name)
    plt.clf()

def read_txt():
    return np.loadtxt(star_catalog)

def get_photon_background_due_to_stars(ra, dec, channel_fov_radius):

    ph_cts = pandas.read_csv(star_photon_counts, names=['ra', 'dec', 'ph_cts', 'ph_cts_arc_sec2'])

    ra_ = int(round(round(ra)/5)*5)
    dec_ = int(round(round(dec)/5)*5)
    queryStr = "ra==" + str(ra_) + " and dec==" + str(dec_)

    star_counts = ph_cts.query(queryStr)['ph_cts'].values[0]
    grid_fov_radius = 2.82  # this value will give fov of ~25 square degrees
    star_counts = (star_counts/get_fov(grid_fov_radius))*get_fov(channel_fov_radius)

    #import ipdb;ipdb.set_trace() # debugging code

    return star_counts

def create_gpose_lightcurve(grb_mag, sky_background, ra, dec, channel_fov_radius, telescope_radius, gap_efficiency, profile, del_time):

    sky_bk_ph_rate = get_photon_rate_from_mag_v(sky_background)*(get_fov(channel_fov_radius)/get_fov(arcSecToDeg))
    sky_bk_ph_rate_std_dev = np.sqrt(sky_bk_ph_rate)

    min_time = 0
    max_time = 16

    #radius = 3 #inch
    area = np.pi * (telescope_radius * inch2m)**2.0

    time = np.arange(min_time, max_time, del_time)

    """
    # insert background stars
    star_num = 0
    max_mag = 6
    min_mag = 0
    #star_arr = (max_mag - min_mag) * np.random.random_sample(star_num) + min_mag
    #star_arr = [-1.46, -0.72, -0.27, -0.04, 0.03, 0.08, 0.12, 0.38, 0.46, 0.50, 0.61, 0.76, 0.77, 0.85, 0.96, 0.98,
    #            1.14, 1.16, 1.25, 1.25, 1.35, 1.50, 1.57, 1.63, 1.63]
    star_arr = read_txt()
    #star_arr = np.array(star_arr[:star_num])
    star_counts = 0.0
    for star_mag in star_arr:
        #print "Background star magnitude: ", star_mag
        star_counts = star_counts + get_photon_rate_from_mag_v(star_mag)  # counts/sec

    #print "Total count: ", -2.5 * np.log10((10**(-0.4*star_arr)).sum())
    #print "Sky Area: ", np.log10(get_fov(10.0)/get_fov(arcSecToDeg)*np.pi)*2.5
    #print "Star Counts: ", star_counts
    star_counts = (star_counts/get_fov(10.0))*get_fov(channel_fov_radius)
    """

    # get the photon background from stars at given ra, dec in the V band
    star_counts = get_photon_background_due_to_stars(ra, dec, channel_fov_radius)

    sky_bk_ph_rate = (sky_bk_ph_rate + star_counts) * del_time * gap_efficiency
    sky_bk_ph_rate_std_dev = np.sqrt(sky_bk_ph_rate)

    rate = sky_bk_ph_rate + np.random.randn(len(time)) * sky_bk_ph_rate_std_dev

    # insert GRB prompt optical emission
    index = int(5.0/del_time)

    # 2 second prompt optical profile
    prompt_opt_profile = [-3.0, -1.9, -0.5,  0.0, -0.1,
                          -0.6, -0.9, -0.9, -0.5, -0.6,
                          -0.8, -0.1,  0.0,  0.0, -0.2,
                          -0.3, -0.5, -2.9, -2.9, -3.0]

    if profile == 2.0:
        prompt_opt_profile = [-3.0, -2.5, -2.5, -2.0, -2.0,
                              -1.5, -1.5, -1.0, -1.0, -0.5,
                              0.0, 0.0,  -0.5, -1.0, -1.0,
                              -2.0, -2.0, -2.5, -2.5, -3.0]

    if profile == 3.0:
        prompt_opt_profile = [0.0, -0.5, -0.5, -1.0, -1.0,
                              -1.5, -1.5, -2.0, -2.5, -2.5,
                              -2.6, -2.6, -2.6, -2.7, -2.7,
                              -2.8, -2.8, -2.8, -2.9, -3.0]

    time_opt_profile = np.linspace(0.0, 2.0, num=20, endpoint=True)
    func = interp1d(time_opt_profile, prompt_opt_profile, kind='cubic')

    time_opt = np.arange(0.0, 2.0, del_time)
    prompt_opt = func(time_opt)
    #import ipdb;ipdb.set_trace() # debugging code

    for opt in prompt_opt:
        rate[index] = rate[index] + get_photon_rate_from_mag_r(grb_mag - opt) * del_time
        index = index + 1

    rate = rate * area
    rateErr = np.sqrt(rate * area)

    return time, rate, rateErr


if __name__ == '__main__':

    read_txt()

    #bat_fov = [10, 20, 30, 40]
    #pmt_fov = [0.25, 0.5, 1, 2, 3, 4, 5, 6]

    #for item1 in bat_fov:
    #    for item2 in pmt_fov:
    #        print "BAT FoV: " + str(item1) + " deg, PMT FoV: " + str(item2) + " deg, Number of PMTs needed: " + str(int(get_fov(item1)/get_fov(item2)))

    print 'Number of telescopes: ', get_fov(60.0)/get_fov(7.0)

    print 'Number of GAP channels: ', get_fov(7.0)/get_fov(0.85)

    print "Counts rate (ph/s/m^2) from R=20 star: ", get_photon_rate_from_mag_r(20.0)

    print "Counts rate (ph/s/m^2) from V=20 star: ", get_photon_rate_from_mag_v(20.0)

    print "Counts for sky bk calculation: ", get_fov(0.85)/get_fov(arcSecToDeg)

    print "Counts rate (ph/s/m^2) from V=21.5 star: ", get_photon_rate_from_mag_v(21.5)

    sky_bk_ph_rate = get_photon_rate_from_mag_v(sky_background)*(get_fov(telescope_fov)/get_fov(arcSecToDeg))
    sky_bk_ph_rate_std_dev = np.sqrt(sky_bk_ph_rate)

    print "Counts rate (ph/s/m^2) from V=21.5 sky brightness: ", sky_bk_ph_rate

    print "Counts rate std. dev. (ph/s/m^2) from V=21.5 sky brightness: ", sky_bk_ph_rate_std_dev

    print "Counts rate (ph/s/m^2) from R=16 star: ", get_photon_rate_from_mag_r(16.0)

    print "Counts rate (ph/s/m^2) from R=15 star: ", get_photon_rate_from_mag_r(15.0)

    print "Counts rate (ph/s/m^2) from R=14 star: ", get_photon_rate_from_mag_r(14.0)

    print "Counts rate (ph/s/m^2) from R=13 star: ", get_photon_rate_from_mag_r(13.0)


    """
    time1, rate1, rateErr1 = create_gpose_lightcurve(14)
    time2, rate2, rateErr2 = create_gpose_lightcurve(13)
    time3, rate3, rateErr3 = create_gpose_lightcurve(12)
    time4, rate4, rateErr4 = create_gpose_lightcurve(11)
    time5, rate5, rateErr5 = create_gpose_lightcurve(10)

    title = "GPOSE LCs"
    plot_file = "gpose_lc.pdf"

    #plot_lightcurve_bar_array([time1, time2, time3, time4, time5],
    #                          [rate1, rate2, rate3, rate4, rate5],
    #                          ['GRB mag: 14', 'GRB mag: 13', 'GRB mag: 12', 'GRB mag: 11', 'GRB mag: 10'],
    #                          title, "Time", "Count Rate (10$^6$ counts/sec)", plot_file)

    plot_lightcurve_bar_array([time1, time2, time3, time4],
                              [rate1, rate2, rate3, rate4],
                              ['GRB mag: 14', 'GRB mag: 13', 'GRB mag: 12', 'GRB mag: 11'],
                              title, "Time", "Count Rate (10$^6$ counts/sec)", plot_file)
    #"""

    #import ipdb;ipdb.set_trace() # debugging code

    #plot_pbh_spectrum()
