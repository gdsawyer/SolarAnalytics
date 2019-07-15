#!/usr/bin/env python3
#
#	SolarPos.py -- compute the position of the sun using Astromonical Algorithm (Michalsky) method
#	Gregory D Sawyer
#	2019-07-03
#	Version v0.1.0
#
#	This is basically being run off the FORTRAN code, but we will break this up 
#	a bit so we can call some of the functions independently
#
#	Import the math library such that we do not have to prefix the math 
#	functions with a package.  
#
from math import *
import datetime
from dateutil import tz


#
#	C O N S T A N T S   A N D   D E F S
#
#	Base Epoch in this case is the Julian RD Epoch which
#	we are setting to the CC3 value for Julian.  We
#	can adjust this value to be any epoch. 
#



def jdFromMoment(aMoment):
	#
	#	(datetime)aMoment:  The date and time we wish to convert to 
	#		a julian day value.
	#
	#	We are going to create a julian day value that will include 
	#	the fractional date of the moment.  Since datetime objects 
	#	will give us what Calendrical Calculations (CC3) would call
	#	a 'rata die' (a value that counts whole days starting at
	#	Gregorian 0001-01-01), we can use that to generate the base
	#	Julian Day value by adding an offset value in days to the 
	#	datetime ordinal.  Then we can tack on the fraction of the 
	#	by extracting the timeparts, converting them to seconds and 
	#	computing the fraction of day.  NOTE the jd we create has only
	#	seconds precision.
	#
	
	
	julianDay = aMoment.toordinal() 
	julianDay += (aMoment.hour * 3600 + aMoment.minute * 60 + aMoment.second ) / 86400
	julianDay += 1721424.5
	
	return julianDay







def solarPositionFor(obsDateTime, obsLatitude, obsLongitude):
	#
	#	(datetime)obsDateTime --  the date and time of the observation
	#	(float)obsLatitude -- The latitude of the observer
	#	(float)obsLongitude -- the longitude of the observer
	#
	#	This is a more-or-less verbatim translation of Michalsky's paper 
	#	that describes the Astronomical Almanac's method for determining
	#	the sun's position in the sky given a date and time of observation.
	#	Michalky broke things up into a lot of intermediate values, and 
	#	that's what I intend to do here.  (Hence "Verbatim".)
	#	Because Python's datetime object can describe itself in a way
	#	that can be readily converted into a JDN, we will not perform
	#	that first conversion step here.
	#
	#	NOTE:  Machalsky's calculations are all in Degrees, so we 
	#	will convert to radians on the way into the trig functions.
	#
	#	NOTE:  obsDateTime must be a TZ aware datetime object where TZ
	#		is set to the timezone where the observation occured.  This 
	#		is necessary in order to correctly compute UT out of the 
	#		database.	
	#
	#
	#	Initial
	#	Check the observation date time to see if it has Time Zone info
	#		by checking the name.  If not, raise a value error.
	#
	#	Get the UTC decimal hour by pulling the hour and minute elements
	#		out of the hour and minute value from the observation datetime's
	#		UTC time, then form a decimal hour
	#
	#	Generate a Julian Day (JD) from the observation date time as a moment
	#		(JDN plus fractional day), then calculate the j2000 epoch based 
	#		moment (the moment counting from 2000-01-01)
	#
	
	if obsDateTime.tzname == None:
		raise ValueError("Observation datetime is missing timezone info")
	
	#
	#  E L S E
	#
	obsJd = jdFromMoment(obsDateTime)
	obsJ2000Moment = obsJd - 2451545.0
	obsJ2kMomentUT = jdFromMoment(obsDateTime.astimezone(tz=datetime.timezone.utc)) - 2451545.0
	
	
	obsUtcDeciHour = obsDateTime.utctimetuple()[3] + obsDateTime.utctimetuple()[4] / 60.0
	
	#	Ecliptic Coordinates
	#
	#	To calculate the position of the sun in the ecliptic orbit, 
	#	we will work with the j2000-based epoch value of the observation
	#	date-time.  Astromomers love this :-)
	#	Then compute the ecliptic lat/long, which is where the
	#	sun is in the orbital ecliptic -- this is the path the 
	#	earth takes as it orbits the sun.  The anomaly is changed
	#	to radians per the FORTRAN.
	#	The obliquity is the "tilt" of the earth, the number of 
	#	degrees the earth is tilted off the ecliptic.  
	#
	#	This will give us what we need to compute the declination
	#	and right ascension of the sun.
	#	NOTE we will convert everything to Radians to aid with computations
	#
	meanLongitude = (280.460+.9856474 * obsJ2kMomentUT) % 360
	if meanLongitude < 0:
		meanLongitude += 360
	#meanLongitude = radians(meanLongitude)
	
	meanAnomaly = (357.528 + 0.9856003 * obsJ2kMomentUT) % 360
	if meanAnomaly < 0:
		meanAnomaly += 360
	meanAnomaly = radians(meanAnomaly)
	
	
	#
	#	Ecliptic Longitude is the position of the sun along the ecliptic
	#	plane.  This should already be in rads because everything going into it
	#	is in rads
	#
	
	
	eclipticLongitude = (meanLongitude + 1.915 * sin(meanAnomaly) * 0.020 * sin(2 * meanAnomaly)) % 360
	if eclipticLongitude < 0:
		#eclipticLongitude += (2*pi)
		eclipticLong += 360
	
	eclipticLongitude = radians(eclipticLongitude)
	
	
	#
	#	Obliquity is the tilt of the Earth in relation to the ecliptic
	#	Nominally 23 degrees but it varies slightly over the course of 
	#	the year
	#
	
	obliquity = radians(23.439 - 0.0000004 * obsJ2kMomentUT)
	
	
	
	#	Celestial Coordinates
	#
	#	In this coordinate system, "lat/long" is called declination
	#	and right ascension respectively.  This brings the coords 
	#	down to a more earthly point of view.
	#	This particular code was lifted from the FORTRAN program
	#	included in Michalsky's paper.  However, I'm adding a 
	#	converstion back to degrees.  (I know, we should make
	#	this entire thing Radians, but...)
	#
	numerator=cos(obliquity)*sin(eclipticLongitude)
	denominator=cos(eclipticLongitude)
	
	raRadians = atan(numerator/denominator)
	if denominator < 0:
		raRadians += pi

	if numerator < 0 and denominator >= 0:
		raRadians += (2 * pi)
	
	rightAscension = degrees(raRadians)
	
	#
	#	The FORTRAN comments says this calculation of declination will
	#	come out in radians (which it does :-) so convert it back to 
	#	degrees. 
	#
	
	declination = asin(sin(obliquity) * sin(eclipticLongitude)) #% (2 * pi)
	
	#
	#	from here we will calculate the mean sidereal time at
	#	Greenwich.  To do that we will extract the hours out of
	#	the observation datetime object and convert to UTC.
	#	TECHNICALLY UTC != UT, which is what they call for here,
	#	but UTC is supposed to be within a second of UT so we'll
	#	go with that.
	#	
	#
	
	
	gmSiderealTime = (6.697375 + 0.0657098242 * obsJ2kMomentUT + obsUtcDeciHour) % 24
	if gmSiderealTime < 0:
		gmSiderealTime += 24
	
	#
	#	Compute the local mean sidereal time
	#	Similar to the above.  The article calls for this being
	#	calculated in east longitude, so we will fiddle with the
	#	long to get it into that format.  If the longitude comes
	#	in less than 0, then we will add (which is subtract) that
	#	value from 360.  They also want this in Radians
	#
	
	lmSiderealTime = (gmSiderealTime + obsLongitude / 15) #% 24
	if lmSiderealTime < 0:
		lmSiderealTime += 24
	
	lmSiderealTime = radians(lmSiderealTime * 15)
	
	
	
	#
	#	Compute the hour angle, which has to be
	#	between 0 and 2pi.  (Note if attempting
	#	a computation in DMS, change "raRadians"
	#	to "rightAscension")
	#	
	
	
	#hourAngle = (lmSiderealTime + raRadians) 
	hourAngle = lmSiderealTime - raRadians
	if hourAngle < -pi:
		hourAngle += (2 * pi)
	
	if hourAngle > pi:
		hourAngle -= (2 * pi)
	
	
	#
	#	Now calculate azimuth and elevation
	#	For convenience, we'll convert the observation latitude
	#	over to radians
	#
	obsLatRadians = radians(obsLatitude)
	elevation = asin(sin(declination) * sin(obsLatRadians) + cos(declination) * cos(obsLatRadians) * cos(hourAngle))
		
	azimuth = asin(-cos(declination)* sin(hourAngle)/cos(elevation)) 
	
	#
	#	Have to do some corrections at this point
	#
	if (sin(declination) - sin(elevation) * sin(obsLatRadians)) >= 0:
		if sin(azimuth) < 0:
			azimuth += (2*pi)
	else:
		azimuth = pi - azimuth
	
	#criticalElevation = asin(sin(declination)/sin(obsLatRadians))
	#if elevation >= criticalElevation:
	#	azimuth = pi - azimuth
	#if (elevation <= criticalElevation) and (hourAngle > 0):
	#	azimuth = 2 * pi + azimuth
	
	#
	#	Now convert everything to degrees
	#
	#hourAngle = degrees(hourAngle)
	#declination = degrees(declination)
	elevation = degrees(elevation)
	azimuth = degrees(azimuth)
	#
	# Return the data as a list in (X,Y) order
	#azimuth is x, elevation is y.  (Elevation is a 
	#function of azimuth.)
	#
	return [azimuth, elevation]
	
	
if __name__ == '__main__':
	testTime = input("What is the time you wish to test? ")
	
	dtTest = datetime.datetime.fromisoformat(testTime)
	dtTest = dtTest.replace(tzinfo=tz.tzlocal())
	
	solarCoords = solarPositionFor(dtTest, 47.638165, -122.389039)
	
	print("Solar position is Azimuth {0} Elevation {1}".format(solarCoords[0], solarCoords[1]))