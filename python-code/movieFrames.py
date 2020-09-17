#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 11:47:23 2020

Making Movies !!

@author: val
"""
#  read in pickled whale and boat data and then run analysis

import os
import os.path
from os import path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import math
from jdcal import gcal2jd, jd2gcal
import pickle

from matplotlib import image    # routines for displaying orca image
from scipy import ndimage
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

os.chdir("/home/val/Documents/NFWF_Files/2020_Analysis/")
print("Working directnp.arctanory is ",os.getcwd())

import WhaleBoatObj   # NOTE BENE these python files have to be in the same directory as this file itself
import whalePlot
import helpers

import globalParameters as gp    ##  gp stands for Global Parameters

########################################################################################
anonBoatsDict = helpers.load_obj("anonimizer")
boatsDict     = helpers.load_obj("boats")
codeCountDict = helpers.load_obj("counts")
activityCodeDict  = helpers.load_obj("activityCode")    
jascoCodesDict = helpers.load_obj("jascoCodes")
echoSL_Dict = helpers.load_obj("echoSL")
  
#anonBoatsDict['CSMINF_168']              #  here NFWF's id 'pow' is anonomized as CSMINF_168
                                          #     where 'pow' is a Commercial Small Inflatable with JASCO code JRHIB
#('pow_CSMINF', 'Commercial Small Inflatable', 'JRHIB', 'Prince of Whales')
#given the anonimized name, the rest of this vehicle's details can be found via boatsDict
#
#boatsDict['CSMINF']  # pull the vessel code off of the numbered code and use it to get the rest of the boat info
# ('Commercial Small Inflatable', 'JRHIB')

#boatType = boatsDict[boatID.split('_')[0]][1]

boatList = [*boatsDict]
boatTypes = []
for boat in boatList:
  typ = boatsDict[boat][1]
  print("boat is",boat, "typ=",typ)
  if not typ in boatTypes:
    print("     Adding ",typ," to boatTypes list")
    boatTypes.append(typ)

#  Figure out how to make the Foraging range an ellipse and point it in the velcity direction

def getForagingEllipse(xWhale, yWhale, forageRange, headingRad, alph):
  degRad = 3.14159/180
  wd = forageRange/2  #  set up for an ellipse
  dx = (forageRange - wd)*np.sin(headingRad)/1.5
  dy = (forageRange - wd)*np.cos(headingRad)/1.5
  xyEllipse = [xWhale+dx, yWhale+dy]
  #print(xWhale, dx, yWhale, dy, xyEllipse)
  return Ellipse(xy=xyEllipse,width=wd,height=forageRange, angle=-headingRad/degRad, ec='blue', alpha = alph)

def getDBcolor(idx):
  if idx==0: return 'red'
  if idx==1: return 'green'
  if idx==2: return 'yellow'
  if idx==3: return 'blue'

def getBoatCircles(xBoat, yBoat, SL):   #return circles successively smaller from dB background to SL at boat
  Ncircles = len(gp.boat_dBlevels)
  dbCircles = []
  R = np.zeros(Ncircles)
  for i in range(Ncircles):
    R[i] = pow(10,-(SL - gp.boat_dBlevels[Ncircles - 1 -i])/gp.spreadingLaw)   # start with largest circles
    
    clr = getDBcolor(Ncircles - i - 1)
    alp = 0.1 + i/10
    dbCircles.append(plt.Circle((xBoat, yBoat), R[i], color=clr, lw = 3, fill = True, alpha=alp))

  return dbCircles

allPassbys = helpers.load_obj("tracksModel_RLs_2003_2005")  # this is list of passbys where each passby is one whale object 
                                                        #      and objects for accompanying boats
def makeMovieFrames(whale, boats, idx, plt):
  fig, ax = plt.subplots()
  plt.rcParams["figure.figsize"] = [16,16]   
  theDate = WhaleBoatObj.getDateFromJulian(whale.jDay[0])
  
  xMean = np.mean(whale.xMod)
  yMean = np.mean(whale.yMod)
  delta = max((max(whale.xMod) -  min(whale.xMod)), (max(whale.yMod) - min(whale.yMod))) 
  xCenter = xMean
  yCenter = yMean
  ax.set_xlim(xCenter-delta,xCenter+delta)
  ax.set_ylim(yCenter-delta,yCenter+delta)
  xScale = [xCenter - 50, xCenter + 50]
  yScale = [yCenter+delta - 0.05*delta, yCenter+delta - 0.05*delta]
  plt.plot(xScale,yScale,linewidth=2,color='black')
  plt.text(xCenter-50, yCenter+delta - 0.035*delta, '100 m' )
  
  timeInSecs = (whale.tModSecs[idx] -  whale.tModSecs[0])*3600*24
  timeCntr = "Time in passby is %0.1f seconds" % timeInSecs
  plt.text(xCenter+0.5*delta, yCenter+delta - 0.030*delta, timeCntr)
  
  plt.text(xCenter+0.5*delta, yCenter+delta - 0.075*delta, 'blue    : Background -> 110 dB')
  plt.text(xCenter+0.5*delta, yCenter+delta - 0.100*delta, 'yellow :   110 -> 120 dB')
  plt.text(xCenter+0.5*delta, yCenter+delta - 0.125*delta, 'green  :   120 -> 130 dB')
  plt.text(xCenter+0.5*delta, yCenter+delta - 0.150*delta, 'red      :    > 130 dB')
  
  plt.text(xCenter+0.5*delta, yCenter+delta - 0.200*delta, 'blue ellipses represent available foraging')
  plt.text(xCenter+0.5*delta, yCenter+delta - 0.225*delta, '  space in front of the whale')
  plt.text(xCenter+0.5*delta, yCenter+delta - 0.250*delta, '  light blue is maximum possible')
  
  
  plotTitle = "%d_%d_%d_%d_%d_%d -" % (theDate)
  plotTitle += " passby number %d" % whale.trackID
  plotTitle += " # boats %d, moving %d, focal whale is %s" % (whale.nBoats, whale.nBoatsMoving, whale.whaleID)
  plt.title(plotTitle)
 
  xW = whale.xMod[idx]
  yW = whale.yMod[idx]

  vxW = whale.vxMod[idx]  
  vyW = whale.vyMod[idx]
  vxW = whale.xMod[idx] - whale.xMod[idx-1]
  vyW = whale.yMod[idx] - whale.yMod[idx-1]    #  Note Bene  Don't forget to follow the v problem down !!!!!!  what is wrong with vxMod ????
  
  xWhaleTrack.append(xW)
  yWhaleTrack.append(yW)
  
  plt.scatter(np.asarray(xWhaleTrack), np.asarray(yWhaleTrack), marker='.', s=1)
  
  for boat in boats:
    xB = boat.xMod[idx]
    yB = boat.yMod[idx]
    SL = boat.SL[idx]
#    print("boat_ID=",boat.boatID, "max SL", np.max(SL))
    bSLcircles = getBoatCircles(xB, yB, SL)
    for bSL in bSLcircles:
       ax.add_artist(bSL)
    # c1 = plt.Circle((xB,yB), 100, color='r', lw = 3, fill = False)
    # ax.add_artist(c1)
    code = boat.boatID   # can use JascoCode or boatCode
    if xB>xCenter-delta and xB<xCenter+delta and yB<yCenter+delta and yB >yCenter-delta:
      plt.text(xB,yB,code)

  phi = math.atan2(vxW,vyW)
  rng = whale.Rforage[idx]
  print(xW,yW,vxW,whale.vyMod[idx],phi,"deg=", phi*180/3.1416, "foraging distance=",rng)
  
  rngMax = whale.RforageMax
  wForagingMax = getForagingEllipse(xW, yW, rngMax, phi, 0.25)
  ax.add_artist(wForagingMax)
  wForaging = getForagingEllipse(xW, yW, rng, phi, 0.75)
  ax.add_artist(wForaging)
  #plt.scatter(xW,yW, color='black')   # this is a dot at location of the whale  
  orcaRotated = ndimage.rotate(orcaImage,-phi*180/3.1416)   # note the angle measures counterclockwise as positive !!!
  zoom = 0.01
  im = OffsetImage(orcaRotated, zoom=zoom)
  ab = AnnotationBbox(im, (xW, yW), xycoords='data', frameon=False)
  ax.add_artist(ab)

  return plt
##################################################################################
whale = allPassbys[80][0]
boats = allPassbys[80][1]

Nframes = len(whale.xMod)
print("Nframes=",Nframes)

orcaImage = image.imread("Orca_1.png")   # image has transparent backgrond !!!

xWhaleTrack = []
yWhaleTrack = []

for idx in range(0, Nframes, 1): ####  Nframes//50):
  makeMovieFrames(whale,boats, idx, plt)   
#  plt.show()  
  plotDirectory = "/home/val/Documents/NFWF_Files/2020_Analysis/frames"
  filename = "%s/img%03d.png" % (plotDirectory, idx)
  plt.savefig(filename)
  plt.show(block=False)  # force plot to write out
  plt.close()
