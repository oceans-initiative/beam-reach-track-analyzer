#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 22:58:34 2020

 conda install -c anaconda numpy 
 conda install -c conda-forge matplotlib 
 conda install -c conda-forge jdcal
@author: val
"""

#  read in pickled whale and boat data and then run analysis

import os
import os.path
from os import path
import numpy as np
import matplotlib.pyplot as plt
import math


os.chdir("/home/val/Documents/NFWF_Files/2020_Analysis/")
print("Working directory is ",os.getcwd())

import WhaleBoatObj   # NOTE BENE these python files have to be in the same directory as this file itself
import whalePlot
import helpers
import globalParameters as gp






#################################################################################
        
allPassbys = helpers.load_obj("tracksModel_2003_2005")  # this is list of passbys where each passby is one whale object 
                                          #      and objects for accompanying boats



def plotRangeToWhale(Ipassby):
  whale = allPassbys[Ipassby][0]
  print(whale)
  if whale.nBoats == 0:
    return
  boats = allPassbys[Ipassby][1]
  rWhale = []
  N100 = N400 = N1000 = N5000 = 0  
  for boat in boats:
    print(boat)
    print("len(rWhale)",len(boat.rWhale))
    for R in boat.rWhale:
      rWhale.append(R)
      if R<100:
        N100 +=1
      if R<400:
        N400 += 1
      if R<1000:
        N1000 += 1
      if R<5000:
        N5000 += 1        
  
  print(f'N100={N100}, N400={N400}, N1000={N1000}, N5000={N5000}')  
  print("min distance to whale=",round(min(rWhale)))
  print("max distance to whale=",round(max(rWhale)))
  if N1000 == 0:
    return
  p100 = int(100*N100/N1000)
  p400 = int(100*N400/N1000)
  pltTitle = f'Passby {whale.trackID} Num boats {whale.nBoats, whale.nBoatsMoving} Min dist {int(min(rWhale))} max dist {int(max(rWhale))}\n%<100={p100} %<400={p400}'  
  # the histogram of the data
  n, bins, patches = plt.hist(rWhale, len(rWhale), density=False, facecolor='g', alpha=0.75)
  plt.title(label=pltTitle)
  plt.xlabel('distance to Whale (m)')  
  plt.xlim(0,1000)
  plt.ylabel('Count')
  plt.grid(True)
  
  
  plotDirectory = "analysisResults"
  filename = "%s/ranges_ID=%d_Nboats=%d_MinMax=%d_%d.png" % (plotDirectory, whale.trackID,len(boats),int(round(min(rWhale))), int(round(max(rWhale))))
  plt.savefig(filename)
  
  #plt.show()
  plt.close()

for i in range(len(allPassbys)):
  plotRangeToWhale(i)


######################################################################################

#Sort passbys by minimum distance boats -> whale
# use itemgetter to select sort key
from operator import itemgetter
distList = []
for passby in allPassbys:
  whale = passby[0]
  boats = passby[1]
  minR = 9999
  thisBoat = ''
  for b in boats:
    thisMin = 9999
    for i in range(len(b.rWhale)):
      if b.rWhale[i]<thisMin:
        thisMin = b.rWhale[i]
        thisBoat = b.boatID
    minR = min(minR,thisMin)
    
  print(whale.trackID,thisBoat,minR)  
  distList.append([whale.trackID, minR, thisBoat])  

distList = sorted(distList,key=itemgetter(1))  # this is list of [trackID, minDistance, closestBoat]

print(distList)

sorted(distList[0:50],key=itemgetter(2))   # sort close approachs by boat that was closest

#####################  a close look at rWhale

npass = 52

p_52 = allPassbys[52]
boats = p_52[1]
for i in range(len(boats)):
  print(i, min(boats[i].rWhale))


ds = map(round,boats[1].rWhale)

plt.plot(ds)


Ipassby = 18
whale = allPassbys[Ipassby][0]
print(whale)

boats = allPassbys[Ipassby][1]
rWhale = []
for boat in boats:
  print(boat)
  print("len(rWhale)",len(boat.rWhale))

  N100 = N400 = N1000 = N5000 = 0  
  for R in boat.rWhale:
    print(R)
    rWhale.append(R)
    if R<100:
      N100 +=1
    if R<400:
      N400 += 1
    if R<1000:
      N1000 += 1
    if R<5000:
      N5000 += 1        


   
      
boatsPassbyList = helpers.load_obj("boatsPassbys_2003_2005")      
scanPassbyList(boatsPassbyList)    # these are boats 

allPassbys = helpers.load_obj("tracksList_2003_2005")

scanPassbyList(allPassbys)
helpers.save_obj(allPassbys,"tracksList_2003_2005")
      
      
      