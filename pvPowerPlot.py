#!/usr/bin/env python3
'''
	pvPowerPlot -- plot the power on the solar position chart
	
	2019-07-13
	Gregory D. Sawyer
	
	This program will extract the power generation observations from the
	energy detail, calculate the solar position in the Horizontal Coordinate
	system using the house's coordinates as reference, and plot the position
	and a nice little dot that shows the amount of power being produced.
	
	The power measure coming out of the database is in watts; Enphase collects
	this data from the array every five minutes, and the power measure is the
	average over that five minute period. 
	
	This program accesses the data out of our PostgreSQL database, it is loaded
	by enphaseDataLoad.py.  We do it this way, instead of accessing the API
	directly, because of the throttling limits imposed by Enphase.  
	
	For plotting, we use Plotly.
	
'''
import sys
import io
import psycopg2
import datetime
from dateutil import tz
from solarPos import solarPositionFor
import plotly
import plotly.plotly as plty
import plotly.graph_objs as grobs
from math import *
import plotly.io as pio

def makeHourLine(xCoord):
	hourLine = dict(type='line', 
		line=dict(color='red',width=1),
		y0=0,
		y1=80,
		opacity=.5)
	hourLine['x0'] = hourLine['x1'] = xCoord
	return hourLine


def makeHourLabel(xCoord, yCoord, labelHour):
	hourLabel = dict(y=yCoord + 3, 
		xref='x', 
		yref='y',
		xshift=8,
		showarrow=False,
		text='{0}h'.format(labelHour),
		x=xCoord)
	if xCoord < 180:
		xCoord = xCoord - 3
		hourLabel['x'] = xCoord
	
	
	return hourLabel
		


def main(generationDate):
	
	#
	#	Some local initiz just for convenience
	#	Sample timezone we will set to local (which at the moment is PT, +8|7 
	#	depending on time of year, and our observation coords.
	#
	
	obsTimezone = tz.tzlocal()
	
	obsPositionLat = 47.638165
	obsPositionLong = -122.389039
	
	
	#
	#	First task is to initialize the DB structures.  Grab a connection then
	#	instantiate a cursor.  Once that is done, execute the SQL to grab the 
	#	data.
	#

	energyDb = psycopg2.connect(host='localhost', user='gdsawyer', database='gdsawyer')
	
	energyCursor = energyDb.cursor()
	
	generationSql = "SELECT gendet.sample_datetime, gendet.power_watts FROM energy.generation_detail gendet WHERE generation_date = %s"
	
	energyCursor.execute(generationSql, (generationDate,))
	
	#
	#	Now we can loop through the cursor and pull out datetime values
	#
	
	plotList = list()
	
	for powerObservation in energyCursor:
		
		sampleDatetime = powerObservation[0].replace(tzinfo=obsTimezone)
		
		solarPosition = solarPositionFor(sampleDatetime, obsPositionLat, obsPositionLong)
		
				
		#
		#	We want to add the power and hour from the sample to the position 
		#	vector before we push that vector onto the plot list.
	
		solarPosition.extend([powerObservation[1], sampleDatetime.hour])
		
		plotList.append(solarPosition)
		
	
	#
	#	Now that we have collected all the data, we can extract x, y and "z"
	#
	
	
	
	xCoord = [obs[0] for obs in plotList]
	yCoord = [obs[1] for obs in plotList]
	colorMap = [obs[2] for obs in plotList]
	plotTitle = 'Power Generation for {0}'.format(generationDate.isoformat())
	
	#
	#	Now we will iterate through the plot list and create the hour lines
	#	and the lables for the hour lines.  This means that hour lines will only
	#	appear where there's actual power.  
	
	hourLines = []
	hourLabels = []
	curHour = None
	
	for plotPoint in plotList:
		#
		#	Don't label the first hour because it is 
		#	usually too close to the second hour (it's)
		#	usually a parital hour.  
		if curHour != plotPoint[3]:
			if curHour == None:
				curHour = plotPoint[3]
			else:
				hourLines.append(makeHourLine(plotPoint[0]))
				hourLabels.append(makeHourLabel(plotPoint[0],plotPoint[1], plotPoint[3]))
				curHour = plotPoint[3]
			
	
	
	trace1 = grobs.Scatter(x=xCoord, y=yCoord, marker={'color':colorMap, 
		'size':10, 
		'colorscale':'Jet', 
		'colorbar':{'title':'Watts'},
		'cmin':0,
		'cmax':4000}, 
		mode='markers',name='powerCurve')
	plotlyLayout=grobs.Layout(title=plotTitle, xaxis={'title':'Azimuth','range':[0,360]},
		yaxis={'title':'Elevation', 'range':[-10,80]},
		#shapes=hourLines,
		annotations=hourLabels,
		plot_bgcolor="#A8B5BE")
		
	myFig = grobs.Figure([trace1], plotlyLayout)
	plotly.offline.plot(myFig)
	fileName = "/Users/gdsawyer/Project/Energy/figure/power_position_{0}.png".format(generationDate.isoformat())
	pio.write_image(myFig, file=fileName,format='png', scale=1)

if __name__ == '__main__':
	#
	#	get the generation date and call the main routine
	#
	inDate = input('Plot for generation date? ')
	
	genDate = datetime.date.fromisoformat(inDate)
	main(genDate)
	
'''

		shapes=[{'type':'line',
			'x0' : 140,
			'y0' : 0,
			'x1' : 140,
			'y1' : 90,
			'line':{'color':'red', 'width':1},
			'name':'10'}],	
'''