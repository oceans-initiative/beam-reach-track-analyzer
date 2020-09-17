#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 10:34:07 2020

@author: val
"""

################################################################  GLOBAL PARAMETERS
workingDirectory = "/home/val/Documents/NFWF_Files/2020_Analysis/"   #  Note Bene:  This MUST be set IN .py file BEFORE imports
modelDeltaSecs = 10   # interval between successive time steps
tortDamping = 6.0
minNumWhaleObs = 4    # need at least this many whale observations to constitute a passby

maxObsGapMins = 15                # any larger gap between whale sitings will start a new whale passby
maxPriorOrPostMinsForBoats = 5   # accept any boat obs from 5 min before focal animal's first fix to 5 min after last one

whaleCVSfileName = "csvFiles/2003_2005_whalePassby.csv"
boatCVSfileName  = "csvFiles/2003_2005_boatPassby.csv"

minNumWhaleObs = 5   # don't save passby with less than 5 whale observations
ff_fileName =  "csvFiles/Whale Activity 2003-2005_EA quality check_FINAL_all_sorted_tabbed.csv"
boatFileName = "csvFiles/All 2003-2005 boat data_EA Quality_Final_sorted_tabbed.csv"       #  Note Bene  MAKE SURE csv FILE SAVED as utf-8 8 bit format 
                                                                                           #  !!!!!!!!!!!!!!  And, delete first two characters if needed

theoTracks_2019_FileName = "csvFiles/FinalTheoTracks_SRKW2019_15April2020_NoErrors.csv"    #  2019 is whale tracks AND (a small number of) boat observations

spreadingLaw = -18
backgroundNoiseLevel = 50 

condenseIfDtLessThan = 10   #  any obs of same target closer together than this parameter are averaged or one is deleted
                            #   15 secs produces 27 boats
                            #   10 secs produces 12 boats

backgroundDb = 100

clickSourceLevel = 170
clickOutwardSpreading = -10
targetCrossSection = 20

callSourceLevel = 150

# parameters for plotting noise from individual boats


boat_dBlevels = [130, 120, 110, backgroundDb]   # change colors for display at ranges where these spreading source levels fall





