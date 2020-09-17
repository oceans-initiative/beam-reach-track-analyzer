#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 16:36:45 2020

@author: val
"""
import numpy as np
from jdcal import gcal2jd, jd2gcal

#######################  GLOBAL PARAMETERS
intervalForDive = 60  # any surfacing more than this # seconds far apart in time signifies the whale has just come up from a dive


#                                     lat           lon         utmE     utmN
# Reference locations:  North site: 48.50935	  -123.1415667   489544  5372925
#                       South site: 48.45701667	-122.9900167   500738  5367098

R_Earth = 6.373e6   # radius of Earth in meters
lat_northSite = 48.50935
lon_northSite = -123.1415667
lat_southSite = 48.45701667
lon_southSite = -122.9900167

utmE_northSite = 489544
utmN_northSite = 5372925
utmE_southSite = 500738
utmN_southSite = 5367098                 

##########################################

################ helpers
def asInt(x):
  try: 
    return int(x)
  except:
    return -99        

def asFloat(x):
  try: 
    return float(x)
  except:
    return -99  
  
def atNorthSite(lat):
  if lat > 48.47:
    return True
  else:
    return False

def calcTortuosity(Xs,Ys, tort):
  for i in range(len(Xs)):
    tort[i] = 0  # first obs has no tortuosity
  if len(tort) > 2:
    for i in range(1,len(tort)-1):
      mag1 = np.sqrt((Xs[i]-Xs[i-1])**2 + (Ys[i]-Ys[i-1])**2)
      mag2 = np.sqrt((Xs[i+1]-Xs[i])**2 + (Ys[i+1]-Ys[i])**2)
#      print(mag2, Xs[i+1]-Xs[i], (Ys[i+1]-Ys[i]))
      rdot = (Xs[i]-Xs[i-1])*(Xs[i+1]-Xs[i]) + (Ys[i]-Ys[i-1])*(Ys[i+1]-Ys[i])
      
      if mag1*mag2 == 0:   # this covers case of two successive obs at exactly same location e.g. 2004/5/11/13:55:57
        theta = 0
      else:  
        x = rdot/(mag1*mag2)
        if x < -1:
          print("calcTort",mag1,mag2,rdot,Xs[i-1],Xs[i],Xs[i+1],Ys[i-1],Ys[i],Ys[i+1], x)
          x=-1
        if x > 1:
          print("calcTort",mag1,mag2,rdot,Xs[i-1],Xs[i],Xs[i+1],Ys[i-1],Ys[i],Ys[i+1], x)
          x = 1
        theta = np.arccos(x)

      tort[i] = 100.0 * np.abs(theta/np.pi)  

#      print("calc tortuosity", i,Xs[i-1],Ys[i-1],Xs[i],Ys[i],Xs[i+1],Ys[i+1],mag1,mag2,rdot, theta*180/np.pi,tort[i])
#      input("check tort??")

def getJulianDay(offset, items):  # items are year, anything, month, day, hour, minute, second  with offset=1 for boat file
  jd = gcal2jd(asInt(items[offset+0]), asInt(items[offset+2]), asInt(items[offset+3]))[1] + (asInt(items[offset+4]) + asInt(items[offset+5])/60 + asInt(items[offset+6])/3600) / 24.0
  return jd  
def getJulianDayNew(yr,mo,dy,hr,mn,sc):  # items are year, anything, month, day, hour, minute, second  with offset=1 for boat file
  jd = gcal2jd(asInt(yr), asInt(mo), asInt(dy))[1] + (asInt(hr) + asInt(mn)/60 + asInt(sc)/3600) / 24.0
  return jd  
def getDateFromJulian(jDay):
  dt = jd2gcal(2400000.5, jDay)
  dayDec = dt[3] - int(dt[3])
  hr = int(dayDec*24)
  minDec = dayDec - hr/24
  minute = int(minDec*60*24)
  sec = int((dayDec*24 - hr - minute/60)*3600)
  return (dt[0],dt[1],dt[2],hr,minute,sec)
  
  

################  
  
class whaleObs(object):  ## receives a list of files that make up the obs of one passby

  def __init__(self, passbyCnt, fileLines):
#YEAR	TrackID	MONTH	DAY	HOUR	MINUTE	SECOND	ID	Sex	Age	Calf	X	Y	meters E	meters N	bearing	distance	longitude	lat	ActivityCode	ActivityState		Site	Original Track ID
#  0     1      2    3   4       5      6     7    8   9  10   11 12   13       14        15        16      17       18      19          20             21            22
    
#2003	7300326	7	30	13	32	37	L57	M	26	No	1615	1563	1476.335393	-1694.587798	138.9374181	2247.486151	-122.969989	48.44176486	4	Travel		South

    self.classType = 'whaleObs'
    self.Nobs = len(fileLines)
    firstLine = fileLines[0]
    items = firstLine.split("\t")  # Tab delimited data file line
    self.trackID = passbyCnt    # this is a counter starting from 0 for each 'detected' passby
    self.trackIDroberin = asInt(items[1])   # this is the original track ID provided by Rob and Erin
 #   if self.trackIDroberin == 7171646:
 #     print(firstLine)
 #     print(self.Nobs)
 #     print(items)
 #     input("??????")
    self.whaleID = items[7]
    self.sex = items[8]
    self.age = asInt(items[9])
    self.jDay  = np.zeros(self.Nobs)
    self.site = items[21]
    self.nBoats = 0
    self.nBoatsMoving = 0
    self.wCalf = np.chararray(self.Nobs, itemsize = 3)   # yes/no signifies Whale traveling with calf
    self.dive = np.zeros(self.Nobs)   # signfies the NEXT interval is a dive
    self.activityState = np.chararray(self.Nobs, itemsize = 10)   #Note  we are not using numeric Activity Code as ait is inconsistent with ActivityState
    self.activityCode  = np.zeros(self.Nobs)
    self.Xroberin = np.zeros(self.Nobs)  # Rob requested that the X and the Y columns in original Excel sheet be maintained
    self.Yroberin = np.zeros(self.Nobs)
    self.utmE  = np.zeros(self.Nobs)
    self.utmN  = np.zeros(self.Nobs)
    self.vE    = np.zeros(self.Nobs)
    self.vN    = np.zeros(self.Nobs)
    self.v     = np.zeros(self.Nobs)
    self.a     = np.zeros(self.Nobs)
    self.tortuosity   = np.zeros(self.Nobs)
    self.latitude  = np.zeros(self.Nobs)
    self.longitude  = np.zeros(self.Nobs)
    i=0
    
    for iFile in range(len(fileLines)):
      items = fileLines[iFile].split("\t")

      self.jDay[i]  = getJulianDay(0,items)
      self.wCalf[i] = items[10]
      self.Xroberin[i] = asInt(items[11])
      self.Yroberin[i] = asInt(items[12])
      lat = asFloat(items[18])
      lon = asFloat(items[17])
      self.latitude[i] = lat
      self.longitude[i] = lon
#
      if lat == -99 or lon == -99:
        self.Nobs = self.Nobs - 1  # skip this observation as lat or lon has bad data
      else:  
        if atNorthSite(lat):
          self.utmE[i] = int(utmE_northSite + (lon - lon_northSite)*(np.pi/180)*R_Earth*np.cos(lat_northSite * np.pi/180))
          self.utmN[i] = int(utmN_northSite + (lat - lat_northSite)*(np.pi/180)*R_Earth)
        else:
          self.utmE[i] = int(utmE_southSite + (lon - lon_southSite)*(np.pi/180)*R_Earth*np.cos(lat_southSite * np.pi/180))
          self.utmN[i] = int(utmN_southSite + (lat - lat_southSite)*(np.pi/180)*R_Earth)
        self.activityCode[i]  = asInt(items[19])
        self.activityState[i] = items[20]  

        if i > 0:
          dtSec = (self.jDay[i] - self.jDay[i-1])*24*3600  # time interval in seconds
          if dtSec == 0:
            self.Nobs = self.Nobs - 1  # skip this observation
            print("jDay not changing", i, iFile, self.trackIDroberin, self.jDay[i],self.jDay[i-1])
          self.vE[i] = (self.utmE[i] - self.utmE[i-1])/dtSec
          self.vN[i] = (self.utmN[i] - self.utmN[i-1])/dtSec
          self.v[i] = np.sqrt(self.vE[i]**2 + self.vN[i]**2)
          ae = (self.vE[i] - self.vE[i-1])/dtSec
          an = (self.vN[i] - self.vN[i-1])/dtSec
          self.a[i] = np.sqrt(ae**2 + an**2)
          if dtSec > 0:
            i += 1    # NOTE BENE:  we only advance i if lat and lon are good and time has changed
        else:
          i += 1
      
    day2sec = 24*3600
    for i in range(self.Nobs-1):
      if (self.jDay[i+1] - self.jDay[i])*day2sec > intervalForDive:
        self.dive[i] = 1   # signifies a long dive from time i to i+1
    if self.Nobs > 1:
      self.vE[0] = self.vE[1]
      self.vN[0] = self.vN[1]
      self.v[0] = self.v[1]
      self.a[0] = self.a[1]
        
    calcTortuosity(self.utmE,self.utmN,self.tortuosity)     
    #  modeled results below
    self.tModSecs = []    
    self.deepdive = []
    self.xMod = []
    self.yMod = []
    self.vxMod = []
    self.vyMod = []
    self.vMod = []
    self.aMod = []
    self.tauMod = []
    self.RL = []
    self.Rcomm = []
    self.Rforage = []
    self.RcommMax = 0
    self.RforageMax = 0
    
  def __repr__(self):
    datetime = getDateFromJulian(self.jDay[0])
    return f'Whale object:\ntrackID={self.trackID}, whaleID={self.whaleID},\n\tDate and Time ={datetime} Number of observations Nobs={self.Nobs}\n\tNumber of boats={self.nBoats}, # moving={self.nBoatsMoving}'

class boatObs(object):  ## receives a list of files that make up the obs of one passby

  def __init__(self, passbyCnt, thisID, fileLines):   # anonomized boatID passed via thisID
#Site	YEAR	TRACK ID	MONTH	DAY	HOUR	MINUTE	SECOND	Boat ID	Boat Code	Boat Code Definition	JASCO Boat Type/Veirs Ship Type	X	Y    	meters E	meters N	bearing	 distance	longitude	lat	Commerical WW Boat Name Where Recorded	NOTES
#  0   1        2      3    4    5      6       7       8        9           10                    11                        12 13       14       15        16        17       18      19      20                                   21

    self.classType = 'boatObs'
    self.Nobs = len(fileLines)
    firstLine = fileLines[0]
    items = firstLine.split("\t")  # comma delimited data file line
    self.site = items[0]
    self.trackID = passbyCnt   
    self.trackIDroberin = asInt(items[2])   # this is the original track ID provided by Rob and Erin
    self.boatID = thisID
    self.boatCode = items[9]
    self.boatDefinition = items[10]
    self.JASCOcode = items[11]
    self.jDay  = np.zeros(self.Nobs)
    self.Xroberin = np.zeros(self.Nobs)  # Rob requested that the X and the Y columns in original Excel sheet be maintained
    self.Yroberin = np.zeros(self.Nobs)
    self.utmE  = np.zeros(self.Nobs)
    self.utmN  = np.zeros(self.Nobs)
    self.vE    = np.zeros(self.Nobs)
    self.vN    = np.zeros(self.Nobs)
    self.v     = np.zeros(self.Nobs)
    self.a     = np.zeros(self.Nobs)
    self.tortuosity   = np.zeros(self.Nobs)
    self.latitude  = np.zeros(self.Nobs)
    self.longitude  = np.zeros(self.Nobs)
    
    for i in range(self.Nobs):
      items = fileLines[i].split("	")
      self.jDay[i]  = getJulianDay(1,items)
      self.Xroberin[i] = asInt(items[12])
      self.Yroberin[i] = asInt(items[13])
      lat = asFloat(items[19])
      lon = asFloat(items[18])
      self.latitude[i] = lat
      self.longitude[i] = lon      
      if lat == -99 or lon == -99:
        print("bad lat or lon data",i,lat,lon, items[12],items[13])
        input("bad boat lat or lon??")
      if atNorthSite(lat):
        self.utmE[i] = int(utmE_northSite + (lon - lon_northSite)*(np.pi/180)*R_Earth*np.cos(lat_northSite * np.pi/180))
        self.utmN[i] = int(utmN_northSite + (lat - lat_northSite)*(np.pi/180)*R_Earth)
      else:
        self.utmE[i] = int(utmE_southSite + (lon - lon_southSite)*(np.pi/180)*R_Earth*np.cos(lat_southSite * np.pi/180))
        self.utmN[i] = int(utmN_southSite + (lat - lat_southSite)*(np.pi/180)*R_Earth)
      
      if i > 0:
        dtSec = (self.jDay[i] - self.jDay[i-1])*24*3600  # time interval in seconds
        self.vE[i] = (self.utmE[i] - self.utmE[i-1])/dtSec
        self.vN[i] = (self.utmN[i] - self.utmN[i-1])/dtSec
        self.v[i] = np.sqrt(self.vE[i]**2 + self.vN[i]**2)
        ae = (self.vE[i] - self.vE[i-1])/dtSec
        an = (self.vN[i] - self.vN[i-1])/dtSec
        self.a[i] = np.sqrt(ae**2 + an**2)      

      if abs(self.utmE[i] - 500000) > 100000:
        print(lat, lon, items)
        input("Something wrong in boat location ---- wait")
    if self.Nobs > 1:
      self.vE[0] = self.vE[1]
      self.vN[0] = self.vN[1]
      self.v[0] = self.v[1]
      self.a[0] = self.a[1]
    calcTortuosity(self.utmE,self.utmN,self.tortuosity)      
    #  modeled results below
    self.tModSecs = []    
    self.deepdive = []
    self.xMod = []
    self.yMod = []
    self.vxMod = []
    self.vyMod = []
    self.vMod = []
    self.aMod = []
    self.tauMod = []
    self.rWhale = []
    self.bearingWhale = []
    self.SL = []
    self.SLcomm = []
    self.SLforage = []
    
  def __repr__(self):
    datetime = getDateFromJulian(self.jDay[0])
    return f'Boat object:\ntrackID={self.trackID}, boatID={self.boatID}, boatDefinition={self.boatDefinition}, JASCOcode={self.JASCOcode}\n\tDate and Time ={datetime} Number of observations Nobs={self.Nobs}'

  def smoothKinematics(self):
    ## now smooth ONLY the magnitude of velocity and acceleration
    vsmooth = [0]
    asmooth = [0]
    if self.Nobs > 3:
      for i in range(1,self.Nobs-1):
        vsmooth.append((self.v[i-1]+self.v[i]+self.v[i+1])/3.0)
        asmooth.append((self.a[i-1]+self.a[i]+self.a[i+1])/3.0)   ### Note Bene:  could calc the a based on the smoothed v !!!!!
      for i in range(1,self.Nobs-1):
        self.v[i] = vsmooth[i]
        self.a[i] = asmooth[i]
      self.v[0] = self.v[1]   # extrapolate the endpoints
      self.v[-1] = self.v[-2]
      self.a[0] = self.a[1]
      self.a[-1] = self.a[-2]      
        
    calcTortuosity(self.utmE,self.utmN,self.tortuosity) 

    