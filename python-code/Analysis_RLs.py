#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:32:23 2020

@author: val
"""

#  read in pickled whale and boat data and then run analysis

import os
import os.path
from os import path
import numpy as np
import matplotlib.pyplot as plt
import math
from jdcal import gcal2jd, jd2gcal
import pickle


os.chdir("/home/val/Documents/NFWF_Files/2020_Analysis/")
print("Working directory is ",os.getcwd())

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
    


#####################################################################################################################

############  Note Bene  Mar. 19, 2020  Need source levels for JPASSENGER and JGOVT_RESEARCH
  
JASCO_SL_Dict = {'J9_9':(136.5074,	11.5002052,	135,	2.38,	4.82),'JCATAMARAN':(137.0507,10.1169774,135,2.22,4.56),'JGOVT_RESEARCH':(137.0507,10.1169774,135,2.22,4.56),'JPASSENGER':(137.0507,10.1169774,135,2.22,4.56),'JRHIB':(135.498,10.2098524,135,2.59,3.94),'JMONOHULL':(135.2181,10.2849913,135,2.66,3.86)} 

Veirs_SL_Dict = {'VMONOHULL': (135,2.79),'VPLEASURE': (135,1.94),'VCARGO': (135,278),'VFISHING': (135,3.19),'VTUG': (135,4.27),'VPASSENGER': (135,2.15), 'VMILITARY': (135,2.34),'KAYAK':(0,0), 'NA':(0,0)}


  
def calcSourceLevel(boatType, mPerSec):  # source levels v dependence follows ECHO/Ross  SL = SLref + C*10*np.log10(V/Vref)
  V = mPerSec * 1.944   # convert to knots
  if boatType in JASCO_SL_Dict:
    a,b,RNL_0, V_0, slope = JASCO_SL_Dict[boatType]
    if V > V_0:
      return a + b * np.log(V)
    else:
      return RNL_0 + slope * V
  if boatType in Veirs_SL_Dict:
    a,b = Veirs_SL_Dict[boatType]
    return a + b*V
  return 0    # return dB   Then import numpy as np and then power = pow(10,sl/10)  and of course dB = np.log10(power)*10



def accumulateReceivedPower(whale, boat, spreadingLaw, DEBUG):  # accumulates power from one boat at all times during passby
  boatType = boatsDict[boat.boatID.split('_')[0]][1]
  smoothedV = []
  #smoothedV = smoothTheVelocity(boat.vMod)
  smoothedV = boat.vMod
  
  for i in range(len(whale.RL)):
    v = smoothedV[i]
    sl = calcSourceLevel(boatType,v)
    boat.SL.append(sl)
    rl = sl + spreadingLaw*np.log10(boat.rWhale[i])
    pwr = pow(10, rl/10)
    whale.RL[i] += pwr
    if DEBUG == 1 and v>0:
      print(boat.trackID, boat.boatID,i,"v=",int(v), "R=", int(boat.rWhale[i]), "RL=", int(rl),"SL", int(sl),"tloss=", int(spreadingLaw*np.log10(boat.rWhale[i])),"dB at whale",int(10*np.log10(whale.RL[i])))
      input("????")
  return

#################################################################################
        
allPassbys = helpers.load_obj("tracksModel_2003_2005")  # this is list of passbys where each passby is one whale object 
                                                        #      and objects for accompanying boats
  
def calculateWhaleRLs(passBy, DEBUG):
  whale = passBy[0]
  boats = passBy[1]
  
#  print(whale.trackID, whale.whaleID)
  #clear whale's RL's and fill with background power
  pwrBackgnd = pow(10,gp.backgroundDb/10)
  whale.RcommMax = pow(10,-(gp.callSourceLevel - gp.backgroundDb)/gp.spreadingLaw)
  whale.RforageMax = pow(10,-(gp.clickSourceLevel - gp.backgroundDb + gp.clickOutwardSpreading + gp.spreadingLaw)/gp.spreadingLaw)
  
  for i in range(len(whale.xMod)):  # add in the background power
    whale.RL.append(pwrBackgnd)

  if whale.nBoats > 0:
    for b in boats:
      if type(b.boatID) == str:
        accumulateReceivedPower(whale, b, gp.spreadingLaw, DEBUG)
        if DEBUG:
          print(b.boatID,"maxDB",10*np.log10(max(whale.RL)))
      
  if len(whale.RL) == 0:
    print("@@@@@@@@@@@@@@@@@@@@@@@  No Data at", whale.trackID)
    return 0
  whale.RL = 10*np.log10(whale.RL)
  whale.Rcomm = pow(10,-(gp.callSourceLevel - whale.RL)/gp.spreadingLaw)
  whale.Rforage = pow(10,-(gp.clickSourceLevel - whale.RL + gp.clickOutwardSpreading + gp.spreadingLaw)/gp.spreadingLaw)
  maxDB = max(whale.RL)
  print("maxDb=",maxDB,"min Rcomm=",min(whale.Rcomm),"min Rforage=",min(whale.Rforage))

  return
  

DEBUG = 0
plotRL = True

def doTest(idx):                           
  passby = allPassbys[idx] 
  maxDb = calculateWhaleRLs(passby,DEBUG)
  whale = passby[0]
  boats = passby[1]
  whalePlot.plotPassby(whale, boats, 500, plotRL,  DEBUG) 
  print("maxDb=",maxDb)

#doTest(80)
# for i in range(20):
#   doTest(i)
  
  
plotRL = True
DEBUG = 0

for passby in allPassbys:
  calculateWhaleRLs(passby,0)
  # whale = passby[0]
  # boats = passby[1]
  # print("trackID",passby[0].trackID,"whale",passby[0].whaleID, "Maximum dB",round(maxDb))
  # whalePlot.plotPassby(whale, boats, 2000, plotRL,  DEBUG) 
  # whalePlot.plotPassby(whale, boats, 1000, plotRL,  DEBUG) 
  # whalePlot.plotPassby(whale, boats, 500, plotRL,  DEBUG) 


helpers.save_obj(allPassbys,"tracksModel_RLs_2003_2005")    # this will update saved allPassbys lists
print("#######################################  ALL DONE")
#acts = []
#for passby in allPassbys:
#    whale = passby[0]
#    for i in range(whale.Nobs):
#        if whale.activityState[i] not in acts:
#            acts.append(whale.activityState[i])
#
#print(acts)
#[b'Forage', b'Travel', b'Rest', b'Socializin', b'Socialize']


