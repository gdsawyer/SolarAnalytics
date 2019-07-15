def meeusSolarPosition(obsDateTime, obsLatitude, obsLongitude):
	#
	#	This is the Meeus interpretation, which I believe is the basis for the 
	#	above function, but more resembles the forumula from Calendrical Calculations
	#	(which I think is based on Meeus' work).  There's a bit more math, a lot 
	#	 more calculations but they appear to be a bit more straight forward.
	#
	#	The process is the same, go from Ecliptic to Equitorial to Horizontal
	#
	#
	#	First, get the time basis.  Meeus uses a century fraction here, based on 
	#	the J2000 epoch, so we will compute that after we pull the JD.  We'll
	#	also check for the tzinfo, and barf if we don't have it.  One note,
	#	CC3 uses 36524 to compute the century fraction...
	#
	#	NOTE:  Most of these calculations output degrees, so we will have to 
	#		be careful about the conversions
	#
	if obsDateTime.tzname == None:
		raise ValueError("Observation datetime is missing timezone info")
	
	#
	#  E L S E
	#
	obsJd = jdFromMoment(obsDateTime)
	obsJ2kMoment = obsJd - 2451545.0
	obsJ2kCentury = obsJ2kMoment / 36525
	utJd = jdFromMoment(obsDateTime.astimezone(tz=datetime.timezone.utc))
	utJ2kMoment = utJd - 2451545.0
	utJ2kCentury = utJ2kMoment / 36525
	
	
	
	print("ObsDate:            ", obsDateTime.isoformat())
	print("obsJd:              ", obsJd)
	print("J2K Moment:         ", obsJ2kMoment)
	print("J2K century:        ", obsJ2kCentury)
	print("UT jd:              ", utJd)
	print("UT J2k Moment:      ", utJ2kMoment)
	print("UT J2k Century:     ", utJ2kCentury)
	
	obsJd = utJd
	obsJ2kMoment = utJ2kMoment
	obsJ2kCentury = utJ2kCentury
	#
	#	First we get the ecliptic coordinates.
	#	We only care about longitude as latitude is assumed to be zero.
	#
	#	New here is the equation of the solar center.
	#
	#	meanAnomaly -- Degrees
	#	meanLongitude -- Degress
	#	solarCenter -- Unknown, but probably radians
	#	eclipticLongitude -- Degrees
	
	meanAnomaly = (357.52910 + 35999.0503 * obsJ2kCentury - 0.0001559 * obsJ2kCentury ** 2 - \
		0.00000048 * obsJ2kCentury ** 3) #Sx% 360
	
	meanLongitude = (280.46645 + 36000.76983 * obsJ2kCentury + 0.0003032 * obsJ2kCentury ** 2) % 360
	
	solarCenter = (1.9146 - 0.004817 * obsJ2kCentury - 0.000014 * obsJ2kCentury ** 2) * \
		sin(radians(meanAnomaly)) + (0.019993 - 0.000101 * obsJ2kCentury) * sin(radians(2 * meanAnomaly)) + \
		0.00029 * sin(radians(3 * meanAnomaly))
	
	eclipticLongitude = meanLongitude - solarCenter
	print("Mean Anomaly:       ", meanAnomaly)
	print("Mean Longitude:     ", meanLongitude)
	print("Solar Center:       ", solarCenter)
	print("Ecliptic Longitude: ", eclipticLongitude)
	#
	#	Equatoral Angles
	#
	#	Here we are going to get Declination and Right Ascension
	#	obliquity -- not sure, but assuming degrees since it's basing
	#		off 23.0 (yes)
	#	X,Y,Z Radians
	#	R -- unknown but assume radians
	#	declinationDelta -- radians
	#	rightAscension -- hours
	#
	
	
	obliquity = (23.0 + 26.0/60.0 + 21.448/3600) - (46.8150 * obsJ2kCentury - 0.00059 * obsJ2kCentury ** 2 + \
		0.001813 * obsJ2kCentury ** 3)/3600
	print("obliquity:          ", obliquity)	
	xRay = cos(radians(eclipticLongitude))
	yAnkee = cos(radians(obliquity)) * sin(radians(eclipticLongitude))
	zUlu = sin(radians(obliquity)) * sin(radians(eclipticLongitude))
	rOmeo = sqrt(1.0 - zUlu**2)
	
	print("X:                  ", xRay)
	print("Y:                  ", yAnkee)
	print("Z:                  ", zUlu)
	print("R:                  ", rOmeo)
	
	
	
	declinationDelta = atan2(zUlu, rOmeo)
	rightAscension = (24/180)* atan2(yAnkee , (xRay + rOmeo))
	
	print("Declination:        ", declinationDelta, degrees(declinationDelta))
	print("Right Ascension:    ", rightAscension, degrees(rightAscension))
	#
	#	Sidereal times
	#
	#	compute the Greenwich Mean Sidereal Time and the Local Mean Sidereal Time
	#	Assuming these units are decimal hours
	#
	
	greenwichSidereal = 280.46061837 + 360.98564736229 * obsJ2kMoment + 0.000387933 * obsJ2kCentury ** 2 - \
		obsJ2kCentury ** 3/38710000.0
		
	localSidereal = greenwichSidereal + obsLongitude
	hourAngle = localSidereal - rightAscension
	
	print("Greenwich:          ", greenwichSidereal)
	print("Local:              ", localSidereal)
	print("Hour Angle:         ", hourAngle)
	#
	#	Horizontal Coords
	#	This is what we want...
	#
	elevation = asin(sin(radians(obsLatitude)) * sin(declinationDelta) + cos(radians(obsLatitude)) + \
		cos(declinationDelta) * cos(radians(hourAngle)))
		
	azimuth = atan(sin(radians(hourAngle)) / (cos(radians(obsLatitude)) * tan(declinationDelta) - sin(radians(obsLatitude)) *
		 cos(radians(hourAngle))))
		 
	#
	#	Print Everything
	#
	print("******Meeus Values******")
	print("Datetime:      ", obsDateTime.isoformat())
	print("JD:            ",obsJd)
	print("J2000 Moment:  ", obsJ2kMoment)
	print("J2000 Century: ", obsJ2kCentury)
	print("Mean Anomaly:  ", meanAnomaly)
	print("Mean Long:     ", meanLongitude)
	print("Solar Center:  ", solarCenter)
	print("Ecliptic Long: ", eclipticLongitude)
	print("Obliquity:     ", obliquity)
	print("X:             ", xRay)
	print("Y:             ", yAnkee)
	print("Z:             ", zUlu)
	print("R:             ", rOmeo)
	print("Declination:   ", declinationDelta)
	print("RA:            ", rightAscension)
	print("GMST:          ", greenwichSidereal)
	print("LMST:          ", localSidereal)
	print("Hour Angle:    ", hourAngle, degrees(hourAngle))
	print("***Elevation:  ", elevation, degrees(elevation))
	print("***Azimuth:    ", azimuth, degrees(azimuth))
	
	
	
