#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 10:19:23 2020

@author: val
"""

#  read in pickled whale and boat data and then run analysis

import os
import os.path
from os import path
import numpy as np
import math
from jdcal import gcal2jd, jd2gcal
import pickle

os.chdir("/home/val/Documents/NFWF_Files/2020_Analysis/")

print("Working directory is ",os.getcwd())

import globalParameters as gp    ##  gp stands for Global Parameters

import WhaleBoatObj
import whalePlot
import helpers

def predictWpositions(w):
  # use utms and observation time intervals to interpolate positions, speeds and tortuosity (tau)
  jDayStart = w.jDay[0]      #use whale's start and stop time to set up time axis
  tStartSecs = (jDayStart - int(jDayStart))*24*3600
  jDayStop = w.jDay[-1]
  tStopSecs  = (jDayStop  - int(jDayStop))*24*3600
  passbySecs = int(tStopSecs - tStartSecs)   # length of observation in seconds
  Npts = int(passbySecs/gp.modelDeltaSecs)
  
  day2sec = 24*3600
  idx = 0
  for i in range(Npts-1):
    tMod = w.jDay[0] + i * gp.modelDeltaSecs/day2sec     # setup time axis for model whale
    while tMod > w.jDay[idx+1] and idx < w.Nobs-2:
      idx += 1
    dt = tMod - w.jDay[idx]
    if w.jDay[idx+1] == w.jDay[idx]:
      print(w.trackID, w.jDay[idx], idx, i, tMod,len(w.jDay), helpers.getDate(w.jDay[idx]))
      input("Likely a row was repeated here by error ??mmm")
      frac = 0
    else:  
      frac = dt/(w.jDay[idx+1] - w.jDay[idx])
    dx = w.utmE[idx + 1] - w.utmE[idx]
    dy = w.utmN[idx + 1] - w.utmN[idx]
    w.tModSecs.append(tMod)
    w.xMod.append(w.utmE[idx] + frac * dx)
    w.yMod.append(w.utmN[idx] + frac * dy)

    if frac<= 0.5:
#      deltat = dt*frac
      arg = -(tMod - w.jDay[idx])/((w.jDay[idx+1] - w.jDay[idx])/gp.tortDamping)
      tortuosity = w.tortuosity[idx-1] * np.exp(arg)  # exponential damping of tortuosity interpolation
    else:
#      deltat = -dt*(1-frac)
      arg = -(w.jDay[idx+1] - tMod)/((w.jDay[idx+1] - w.jDay[idx])/gp.tortDamping)
      tortuosity =  w.tortuosity[idx]*np.exp(arg)
    w.tauMod.append(tortuosity)
    
    #  label as long dive or not  --  project forward the value of w.dive from the beginning of this obs interval (idx)
    w.deepdive.append(w.dive[idx])
    w.vxMod.append(w.vE[idx])
    w.vyMod.append(w.vN[idx])
    w.vMod.append(w.v[idx])
    w.aMod.append(w.a[idx])
  
def predictBpositions(w, b):
  # use utms and observation time intervals to interpolate positions, speeds and tortuosity (tau)
  jDayStart = w.jDay[0]    # Note Bene -- use whale's start and stop time to set up time axis
  tStartSecs = (jDayStart - int(jDayStart))*24*3600
  jDayStop = w.jDay[-1]
  tStopSecs  = (jDayStop  - int(jDayStop))*24*3600
  passbySecs = int(tStopSecs - tStartSecs)   # length of observation in seconds
  Npts = int(passbySecs/gp.modelDeltaSecs)
  
  if b.Nobs > 1:
    print("got multiple obs")
  
  day2sec = 24*3600
  idx = 0
  for i in range(Npts-1):
    tMod = b.jDay[0] + i * gp.modelDeltaSecs/day2sec     # setup time axis for model boat
    b.tModSecs.append(tMod)
    if len(b.jDay) > 1:
      while idx < b.Nobs-2 and tMod > b.jDay[idx+1]:
        idx += 1
##      print(i,idx,"b.Nobs",b.Nobs)  
      dt = tMod - b.jDay[idx]
      frac = dt/(b.jDay[idx+1] - b.jDay[idx])
      dx = b.utmE[idx + 1] - b.utmE[idx]
      dy = b.utmN[idx + 1] - b.utmN[idx]
      
      b.xMod.append(b.utmE[idx] + frac * dx)
      b.yMod.append(b.utmN[idx] + frac * dy)
      if frac<= 0.5:
  #      deltat = dt*frac
        arg = -(tMod - b.jDay[idx])/((b.jDay[idx+1] - b.jDay[idx])/gp.tortDamping)
        tortuosity = b.tortuosity[idx-1] * np.exp(arg)  # exponential damping of tortuosity interpolation
      else:
  #      deltat = -dt*(1-frac)
        arg = -(b.jDay[idx+1] - tMod)/((b.jDay[idx+1] - b.jDay[idx])/gp.tortDamping)
        tortuosity =  b.tortuosity[idx]*np.exp(arg)
      b.tauMod.append(tortuosity)      
      b.vxMod.append(b.vE[idx])
      b.vyMod.append(b.vN[idx])
      b.vMod.append(b.v[idx])
      b.aMod.append(b.a[idx])
    else:
      b.xMod.append(b.utmE[idx])   # we have only one obs of this boat so no info on velocities etc.
      b.yMod.append(b.utmN[idx])
      b.tauMod.append(0)      
      b.vxMod.append(0)
      b.vyMod.append(0)
      b.vMod.append(0)
      b.aMod.append(0)   
    dx = (b.xMod[i] - w.xMod[i])
    dy = (b.yMod[i] - w.yMod[i])
    R = np.sqrt(dx**2 + dy**2)
    theta = 180*math.atan2(dx,dy)/np.pi
    b.rWhale.append(R)
    b.bearingWhale.append(theta)

##  print("leaving predictBpositions")
######################################  Executable code starts here
    
tracksList = helpers.load_obj("tracksList_2003_2005")

for track in tracksList:
  whale = track[0]
  print(whale)predictBpositions
  predictWpositions(whale) 
  boats = track[1]
  for boat in boats:
    print("trackIDs", whale.trackID ,boat.trackID, "predicting boat",boat.boatID, "# boat obs",boat.Nobs)
    predictBpositions(whale, boat)  
    print("check boat xMod len=",len(boat.xMod))
    
  # whalePlot.plotPassby(whale, boats, 2400, False, False)#  Don't plot RLs and no DEBUG
  # whalePlot.plotPassby(whale, boats, 1200, False, False)
  # whalePlot.plotPassby(whale, boats, 600, False, False)
  # whalePlot.plotPassby(whale, boats, 300, False, False)  
  if whale.trackID == 555555:
    break
  
helpers.save_obj(tracksList,"tracksModel_2003_2005")
