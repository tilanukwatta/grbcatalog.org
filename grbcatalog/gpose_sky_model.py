# Sky brightness model from Krisciunas and Schaefer (1991)
# PASP 103, 1033

import numpy

# V band extinction coefficient
k_V = 0.172

# Dark night sky brightness at zenith
muV_zen = 21.587 # mag per square arcsec

# Rayleigh scattering norm
C_R = 2.27e5

def magToNanoLambert(m):
    # V band
    return 34.08*numpy.exp(20.7233 - 0.92104*m)  # eq 1

def nanoLambertToMag(nL):
    # V band
    return (20.7233-numpy.log(nL/34.08))/0.92104  # inverse of eq 1

def airmass(z, method=0):
    # z - zenith distance in deg
    sinz = numpy.sin(z*numpy.pi/180.)
    cosz = numpy.cos(z*numpy.pi/180.)
    if method:
        return 1./(cosz + 0.025*numpy.exp(-11.*cosz))
    return 1./numpy.sqrt(1.0 - 0.96*sinz**2)  # eq 3

def darkSkyNanoLamberts(z, k=k_V, muV_zen=muV_zen):
    X = airmass(z)  # eq 3
    B_zen = magToNanoLambert(muV_zen)
    return B_zen*X*10.**(-0.4*k*(X-1.))  # eq 2

def darkSkyMag(z, k=k_V, muV_zen=muV_zen):
    return nanoLambertToMag(darkSkyNanoLamberts(z, k, muV_zen))

def scatFuncRayleigh(separ):
    cosrho = numpy.cos(separ*numpy.pi/180.)
    return C_R*(1.06+cosrho**2)  # eq 17

def scatFuncMie(separ):
    if separ < 10.:
        return 10.**(6.15-separ/40.)  # eq 18
    else:
        return 6.2e7/separ**2  # eq 19

def magMoon(phase):
    return -12.73 + 0.026*numpy.abs(phase) + 4.e-9*phase**4  # eq 9

def moonSkyMagOld(phase, separ, z_Sky, z_Moon, k=k_V, muV_zen=muV_zen):
    m = 16.57 + magMoon(phase)
    I = 10.0**(-0.4*m)  # eq 8
    scatFunc = scatFuncRayleigh(separ) + scatFuncMie(separ)  # eq 16

    C_Moon = 10.**(-0.4*k*airmass(z_Moon))
    C_Sky  = 1. - 10.**(-0.4*k*airmass(z_Sky))

    B_Moon = scatFunc*I*C_Moon*C_Sky  # nL  eq 15

    B_0 = darkSkyNanoLamberts(z_Sky, k, muV_zen)

    return B_Moon, -2.5*numpy.log10(1.+B_Moon/B_0)  # eq 22

def moonSkyMag(phase, separ, z_Sky, z_Moon, k=k_V, muV_zen=muV_zen):

    I = 10.0**(-0.4*(3.84 + 0.026*numpy.abs(phase) + 4.0e-9 * phase**4))  # eq 20

    rho = separ
    if rho > 10:
        scatFunc = (10.**5.36) * (1.06 + numpy.cos(rho*numpy.pi/180.)**2) + 10.**(6.15-rho/40.0)  # eq 21 and eq 18
    else:
        scatFunc = (10.**5.36) * (1.06 + numpy.cos(rho*numpy.pi/180.)**2) + 6.2e7/(rho**2)  # eq 21 and eq 19

    C_Moon = 10.**(-0.4*k*airmass(z_Moon))
    C_Sky  = 1. - 10.**(-0.4*k*airmass(z_Sky))

    B_Moon = scatFunc*I*C_Moon*C_Sky  # nL  eq 15

    B_0 = darkSkyNanoLamberts(z_Sky, k, muV_zen)

    return B_Moon, -2.5*numpy.log10(1.+B_Moon/B_0)  # eq 22

if __name__ == '__main__':

    #separ = numpy.array([5., 30., 60., 90., 120.])
    #phase = numpy.array([0., 30., 60., 90., 120.])

    separ = numpy.array([120.])
    phase = numpy.array([30., 60., 90., 120.])

    z_Moon = 60.

    for alpha in phase:
        for rho in separ:
            z_Sky = numpy.abs(z_Moon - rho)
            B_moon, dV = moonSkyMag(alpha, rho, z_Sky, z_Moon)
            print "alpha: %6.2f, rho: %6.2f, Z: %6.2f, B_moon: %6.2f, delta V: %10.2f" % (alpha, rho, z_Sky, B_moon, dV)

