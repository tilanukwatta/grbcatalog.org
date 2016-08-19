#!/usr/bin/env python

import numpy as np
import os
import sys
import django
import pandas
import ephem
from django.core.management import setup_environ
import settings
setup_environ(settings)

import gpose_analysis as gpose
import gpose_sky_model as gpose_sky
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import numpy.random as rand
from matplotlib.backends.backend_pdf import PdfPages
import sqlite3
import cPickle

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

cpath = os.getcwd() + '/'
plotpath = "/home/tilan/data/ext_data/gpose/"

# select Swift pointing preference
anti = 1

if anti == 0:
    datapath = "/home/tilan/data/ext_data/gpose/simulation/"
else:
    datapath = "/home/tilan/data/ext_data/gpose/anti_solar_simulation/"

def rad2deg(rad):
    return rad/np.pi*180.0

def deg2rad(deg):
    return deg/180.0*np.pi

def gen_random_numbers(min_num, max_num, grb_number):
    num_list = (rand.random(grb_number) * (max_num-min_num)) + min_num
    return num_list

def get_moon_phase_alpha(phase):
    return (1.0-phase/100.0)*180.0

def get_grb_info(grb_number):
    cdate = datetime.utcnow()
    #cdate = cdate.replace(year=1984, month=5, day=30, hour=16, minute=22, second=56, microsecond=0)
    cdate = cdate.replace(year=2015, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    grb_date_offset = rand.random_integers(0, 264, grb_number) + rand.random(grb_number)
    grb_dates = []
    for offset in grb_date_offset:
        grb_dates.append(cdate + timedelta(days=offset))

    ra_list = gen_random_numbers(0.0, 360.0, grb_number)
    dec_list = gen_random_numbers(-90.0, 90.0, grb_number)

    grb_list = []
    for ra, dec, grb_date in zip(ra_list, dec_list, grb_dates):
        row = [ra, dec, grb_date]
        grb_list.append(row)

    return grb_list

def get_grb_info_anti_solar(grb_number):
    cdate = datetime.utcnow()
    #cdate = cdate.replace(year=1984, month=5, day=30, hour=16, minute=22, second=56, microsecond=0)
    cdate = cdate.replace(year=2015, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    grb_gen_number = 0
    grb_dates = []
    ra_list = []
    dec_list = []
    while grb_gen_number < grb_number:
        # generate a random location on earth to find the night side.
        rand_obs = ephem.Observer()
        rand_obs.epoch = '2000'
        #rand_obs.lon, rand_obs.lat = '-106.68969846', '35.88053854'
        #rand_obs.elevation = 2477
        rand_obs.lon = str(gen_random_numbers(-180, 180.0, 1)[0])
        rand_obs.lat = str(gen_random_numbers(-36.0, 36.0, 1)[0])
        rand_obs.elevation = gen_random_numbers(0, 1000.0, 1)[0]

        # generate a random date and location for a GRB
        grb = ephem.FixedBody()
        date_offset = rand.random_integers(0, 264, 1)[0] + rand.random(1)[0]
        grb_date = cdate + timedelta(days=date_offset)
        grb_ra = gen_random_numbers(0.0, 360.0, 1)[0]
        grb_dec = gen_random_numbers(-90.0, 90.0, 1)[0]
        grb._ra = grb_ra
        grb._dec = grb_dec

        # find the altitude of the Sun and GRB for the random location
        rand_obs.date = grb_date
        sun = ephem.Sun()
        sun.compute(rand_obs)
        altsun = rad2deg(sun.alt)
        #print "Sun Alt Angle: ", altsun
        grb.compute(rand_obs)
        altgrb = rad2deg(grb.alt)
        #print "GRB Alt Angle: ", altgrb

        # select GRBs in anti-solar direction
        if altsun < -45:
            if altgrb > 10:
                grb_dates.append(grb_date)
                ra_list.append(grb_ra)
                dec_list.append(grb_dec)
                #print "grb_gen_number: ", grb_gen_number
                #print "Sun Alt Angle: ", altsun
                #print "GRB Alt Angle: ", altgrb
                grb_gen_number = grb_gen_number + 1
                #import ipdb; ipdb.set_trace() # debugging code
    #import ipdb; ipdb.set_trace() # debugging code

    grb_list = []
    for ra, dec, grb_date in zip(ra_list, dec_list, grb_dates):
        row = [ra, dec, grb_date]
        grb_list.append(row)

    return grb_list

#"""
def create_parameter_combinations():
    sky_background_site_arr = [19.5, 20.5, 21.5, 22.0]
    t90_arr = [2.0, 1.0, 0.5, 0.1, 0.05, 0.01]
    del_time_arr = [0.5, 0.1, 0.05, 0.01]
    grb_mag_arr = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    gpose_radius_arr = [60.0]
    num_telescope_arr = [16, 64]
    num_channels_arr = [16, 64]
    telescope_radius_arr = [3.0, 5.0]
    gap_efficiency_arr = [0.4]
    profile_arr = [1.0, 2.0, 3.0]

    num_para = 10  # modify this if you add more parameters
    para_comb = np.array(np.meshgrid(sky_background_site_arr,
                                     t90_arr,
                                     del_time_arr,
                                     grb_mag_arr,
                                     gpose_radius_arr,
                                     num_telescope_arr,
                                     num_channels_arr,
                                     telescope_radius_arr,
                                     gap_efficiency_arr,
                                     profile_arr)).T.reshape(-1, num_para)

    #import ipdb; ipdb.set_trace() # debugging code
    return para_comb
#"""

"""
def create_parameter_combinations():
    sky_background_site_arr = [21.5]
    t90_arr = [2.0, 1.0, 0.5, 0.1, 0.05]
    del_time_arr = [0.5]
    grb_mag_arr = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    gpose_radius_arr = [60.0]
    num_telescope_arr = [16, 64]
    num_channels_arr = [16, 64]
    telescope_radius_arr = [5.0]
    gap_efficiency_arr = [0.4]
    profile_arr = [3.0]

    num_para = 10  # modify this if you add more parameters
    para_comb = np.array(np.meshgrid(sky_background_site_arr,
                                     t90_arr,
                                     del_time_arr,
                                     grb_mag_arr,
                                     gpose_radius_arr,
                                     num_telescope_arr,
                                     num_channels_arr,
                                     telescope_radius_arr,
                                     gap_efficiency_arr,
                                     profile_arr)).T.reshape(-1, num_para)

    #import ipdb; ipdb.set_trace() # debugging code
    return para_comb
"""

def anti_solar_vs_random(gpose_obs, grb_number, sim_years):
    def cal_nighttime_events(grb_list, gpose_obs):
        sun = ephem.Sun()
        nighttime_visible = 0
        for k in grb_list:
            grb_ra = k[0]
            grb_dec = k[1]
            grb_date = k[2]

            gpose_obs.date = grb_date
            sun.compute(gpose_obs)

            grb = ephem.FixedBody()
            grb._ra = grb_ra
            grb._dec = grb_dec
            grb.compute(gpose_obs)

            zsun = 90.0 - rad2deg(sun.alt)
            z = 90.0 - rad2deg(grb.alt)
            #print "Sun Alt Angle: ", rad2deg(sun.alt)
            #print "GRB Alt Angle: ", rad2deg(grb.alt)
            #print "Sun Zenith Angle: ", zsun
            #print "GRB Zenith Angle: ", z
            #print "\n"

            if zsun > 96:  # night time at GPOSE observatory
                if z < 80:  # GRB is visible at the GPOSE observatory
                    nighttime_visible += 1

        #print "nighttime_visible: ", nighttime_visible
        return nighttime_visible

    num = sim_years
    anti_solar_visibility = []
    random_visibility = []
    for k in range(num):
        if k % 20.0 == 0:
            print 'Year: ', k
        grb_list = get_grb_info(grb_number)
        anti_grb_list = get_grb_info_anti_solar(grb_number)

        anti_nighttime_visible = cal_nighttime_events(anti_grb_list, gpose_obs)
        #import ipdb; ipdb.set_trace() # debugging code
        nighttime_visible = cal_nighttime_events(grb_list, gpose_obs)

        random_visibility.append(nighttime_visible)
        anti_solar_visibility.append(anti_nighttime_visible)

    plt.subplots_adjust(hspace=0.4)
    ax = plt.subplot(111)

    vis_list = []
    for rand, anti in zip(random_visibility, anti_solar_visibility):
        row = [rand, anti]
        vis_list.append(row)

    X = np.array(vis_list)
    print X.shape
    #import ipdb; ipdb.set_trace() # debugging code
    #n, bins, patches = ax.hist(X, 15, color=['red', 'blue'], label=['random', 'anti-solar'], alpha=0.75, histtype='bar', normed=1)
    n, bins, patches = ax.hist(X, 15, color=['red', 'blue'], label=['random', 'anti-solar'], alpha=0.75, histtype='bar')
    plt.legend()

    #ax.set_xlim(xmin, xmax)
    #ax.set_ylim(ymin, ymax)

    plt.title("Simulated Years: " + str(num))
    plt.ylabel("Frequency")
    plt.xlabel("Visible GRB Percentage")
    plt.savefig(plotpath + "anti_solar_vs_rand.pdf", bbox_inches='tight')
    plt.clf()

if __name__ == '__main__':

    # This is the number of GRBs Swift detect per year. Generally GRB happens per day.
    # But this simulation only consider GRBs detected by Swift which is about 30%
    # of all GRBs detectable at Earth.
    grb_number = 100
    #sky_background_site = 21.5
    k_V = 0.172

    gpose_obs = ephem.Observer()
    gpose_obs.epoch = '2000'
    #gpose_obs.lon, gpose_obs.lat = '17.13', '62.56'
    #gpose_obs.lon, gpose_obs.lat = '-84.39733', '33.775867'
    gpose_obs.lon, gpose_obs.lat = '-106.68969846', '35.88053854'
    gpose_obs.elevation = 2477
    sun, moon = ephem.Sun(), ephem.Moon()

    if anti == 0:
        # get the GRB list (no direction preference)
        grb_list = get_grb_info(grb_number)
    else:
        # get the anti-solar GRB list
        grb_list = get_grb_info_anti_solar(grb_number)

    # plot the random vs anti-solar visibility percentages
    anti_solar_vs_random(gpose_obs, grb_number, 1000)
    import ipdb; ipdb.set_trace() # debugging code

    para_comb = create_parameter_combinations()

    index = 1
    results_df = []
    results_labels = ['ra',
                      'dec',
                      'datetime',
                      'sky_background_site',
                      't90',
                      'del_time',
                      'grb_mag',
                      'gpose_radius',
                      'num_telescope',
                      'num_channels',
                      'telescope_radius',
                      'gap_efficiency',
                      'profile',
                      'alpha',
                      'rho',
                      'z',
                      'zmoon',
                      'maxSig',
                      'num10Sig',
                      'num5Sig',
                      'num3Sig',
                      'num2Sig']

    # counters
    cts_total = 0
    cts_nighttime = 0
    cts_nighttime_visible = 0
    cts_daytime = 0
    cts_daytime_visible = 0

    with PdfPages('sig_curve.pdf') as pdf:
        for k in grb_list:
            print "GRB: ", cts_total + 1
            cts_total += 1

            grb_ra = k[0]
            grb_dec = k[1]
            grb_date = k[2]

            gpose_obs.date = grb_date
            sun.compute(gpose_obs)
            moon.compute(gpose_obs)

            grb = ephem.FixedBody()
            grb._ra = grb_ra
            grb._dec = grb_dec
            grb.compute(gpose_obs)
            #print "GRB Location: ", grb.alt, grb.az

            #print "GRB (ra, dec): ", grb_ra, grb_dec
            #print "GRB Time: ", grb_date
            #print("%s %s" % (sun.ra, sun.dec))
            #print("%s %s" % (moon.ra, moon.dec))

            #print("%.12f %.12f" % (rad2deg(sun.ra), rad2deg(sun.dec)))
            #print("%.12f %.12f" % (rad2deg(moon.ra), rad2deg(moon.dec)))

            alpha = get_moon_phase_alpha(moon.phase)  # probably not the correct scaling...need to check this later

            #print "Moon Phase: ", moon.phase, "  Alpha: ", alpha
            #print "Moon Earth Distance: ", moon.earth_distance

            zenith_ra = rad2deg(gpose_obs.radec_of(deg2rad(0), deg2rad(90))[0])
            zenith_dec = rad2deg(gpose_obs.radec_of(deg2rad(0), deg2rad(90))[1])

            #print "Zenith (ra, dec): ", zenith_ra, zenith_dec

            zmoon = 90.0 - rad2deg(moon.alt)

            #print "Moon Zenith Angle: ", zmoon

            zsun = 90.0 - rad2deg(sun.alt)

            #print "Sun Zenith Angle: ", zsun

            z = 90.0 - rad2deg(grb.alt)

            #print "GRB Zenith Angle: ", z

            rho = rad2deg(ephem.separation(grb, moon))

            #print "Angle between the GRB and the moon: ", rho

            if zsun > 96:  # night time at GPOSE observatory
                cts_nighttime += 1
                if not z < 80:  # GRB is visible at the GPOSE observatory
                    cts_nighttime_visible += 1
            else:
                cts_daytime += 1
                if z < 80:  # GRB is visible at the GPOSE observatory
                    cts_daytime_visible += 1

            if zsun > 96:  # night time at GPOSE observatory
                #print "Night time...."
                if z < 80:  # GRB is visible at the GPOSE observatory
                    #print "Night time, GRB is visible...."

                    #for para in para_comb[:5]:
                    for para in para_comb:
                        sky_background_site = para[0]
                        t90 = para[1]
                        del_time = para[2]
                        grb_mag = para[3]
                        gpose_radius = para[4]
                        num_telescope = para[5]
                        num_channels = para[6]
                        telescope_radius = para[7]
                        gap_efficiency = para[8]
                        profile = para[9]

                        if zmoon < 90:
                            bMoon, deltaV = gpose_sky.moonSkyMag(alpha, rho, z, zmoon, k_V, sky_background_site)
                            sky_background = sky_background_site + deltaV  # add the contribution from the moon to the sky background
                        else:
                            sky_background = sky_background_site

                        #"""
                        telescope_fov = gpose.get_fov(gpose_radius)/num_telescope
                        channel_fov = telescope_fov/num_channels
                        channel_fov_radius = gpose.get_fov_radius(channel_fov)

                        #print grb_mag, sky_background, grb_ra, grb_dec, channel_fov_radius, telescope_radius, gap_efficiency, profile, del_time

                        time1, rate1, rateErr1 = gpose.create_gpose_lightcurve(grb_mag,
                                                                               sky_background,
                                                                               grb_ra,
                                                                               grb_dec,
                                                                               channel_fov_radius,
                                                                               telescope_radius,
                                                                               gap_efficiency,
                                                                               profile,
                                                                               del_time,
                                                                               t90=t90)

                        rate = rate1 - np.median(rate1) # use meadian
                        rateSig = rate/rateErr1
                        maxSig = max(rateSig)
                        num10Sig = len(np.where(rateSig > 10.0)[0])
                        num5Sig = len(np.where(rateSig > 5.0)[0])
                        num3Sig = len(np.where(rateSig > 3.0)[0])
                        num2Sig = len(np.where(rateSig > 2.0)[0])

                        """
                        plt.plot(time1, rate1)
                        plt.errorbar(time1, rate1, yerr=rateErr1, ecolor='black', fmt='o')
                        plt.title('Maximum significance: ' + str(round(maxSig, 3)) + ' GRB Mag: ' + str(round(grb_mag, 3)))
                        #plt.title('Maximum significance: ' + str(round(maxSig, 3)))
                        plt.ylabel('Significance')
                        plt.xlabel('Time')
                        plt.tight_layout()
                        pdf.savefig()
                        plt.close()
                        index = index + 1
                        #"""
                        # compile simulation parameters for saving
                        df_row = [grb_ra, grb_dec, grb_date] \
                                 + list(para) + [alpha, rho, z, zmoon]\
                                 + [maxSig, num10Sig, num5Sig, num3Sig, num2Sig]
                        #print df_row
                        results_df.append(df_row)
                        #import ipdb; ipdb.set_trace() # debugging code
                    #print "\n"
                    #break
            print "\n"

    # print the value of the counters.
    print "cts_total: ", cts_total
    print "cts_nighttime: ", cts_nighttime
    print "cts_nighttime_visible: ", cts_nighttime_visible
    print "cts_daytime: ", cts_daytime
    print "cts_daytime_visible: ", cts_daytime_visible
    print "\n"

    simdata = pandas.DataFrame(results_df, columns=results_labels)

    filename = 'gpose_simulation.dat'

    data_file = open(datapath + filename, 'wb')
    cPickle.dump(simdata, data_file)
    data_file.close()

    """
    filename = 'gpose_simulation.csv'
    simdata.to_csv(datapath + filename, index=False)

    filename = 'gpose_simulation.db'
    conn = sqlite3.connect(datapath + filename)
    simdata.to_sql('gpose_simulation', conn, flavor='sqlite', if_exists='replace', index=False)
    conn.close()
    """


    #import ipdb; ipdb.set_trace() # debugging code




