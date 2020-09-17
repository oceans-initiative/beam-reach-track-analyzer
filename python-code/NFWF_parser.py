#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 5 12:42:22 2020

Read NFWF whale and boat observation files and 
   create Julian Date identifies and detect passbys in whale file.
   Then, find corresponding boat observations and 
   build and save Whale and Boat datastructures for each passbby

@author: val
"""
import os.path
from os import path
import numpy as np
#from jdcal import gcal2jd, jd2gcal
import helpers
import globalParameters as gp
import WhaleBoatObj
###################################################################
# Scan Ocean Initiative csv file(s) and construct whale and boats passby and tracks lists
#csv file structure
# YEAR	TrackID	MONTH	DAY	HOUR	MINUTE	SECOND	ID	Sex	Age	Calf	X	Y	meters E	meters N	bearing	distance	longitude	lat	ActivityCode	ActivityState	Site	Original Track ID
# 2003	7300501	7	30	5	9	24	J1	M	52	No	870	1715	597.5052301	-1827.871029	161.8981624	1923.050961	-123.1334529	48.49290019	5	Forage	North	
# 2003	7300501	7	30	5	10	20	J1	M	52	No	856	1552	492.1463197	-1702.713129	163.8787737	1772.410788	-123.1348834	48.49402661	5	Forage	North	

# Output data file structure:
# classtype	trackID	trackIDroberin	site	whaleID	age	year	month	day	hr	minute	sec	jDay	wCalf	activityCode	ActivityState	Xroberin	Yroberin	latitude	longitude	utmE	utmN	vE	vN	v	a	tortuosity
# whaleObs	0	7300501	North	J1	52	2003	7	30	5	9	24	52850.2148611	No	5	Forage	870	1715	48.492900	-123.133453	490141	5371095	-1.875	2.232	2.915	0.052	0.000
# whaleObs	0	7300501	North	J1	52	2003	7	30	5	10	20	52850.2155093	No	5	Forage	856	1552	48.494027	-123.134883	490036	5371220	-1.875	2.232	2.915	0.052	2.593

# Xroberin and Yroberin   Note: Rob requested that the X and the Y columns in original Excel sheet be maintained

# save_CVS_format(whalePassbyList, boatsPassbyList)
# helpers.save_obj(whalePassbyList,"whalePassbys_2003_2005")  
# helpers.save_obj(boatsPassbyList,"boatsPassbys_2003_2005")
# helpers.save_obj(tracksList,"tracksList_2003_2005")   


### Note Bene  -- IMPORTANT globals  ****************************************************************************

parseErrorFileName = "analysisResults/parseErrors.txt"
parserLogFileName  = "analysisResults/parserLog.txt" 

os.chdir("/home/val/Documents/NFWF_Files/2020_Analysis/")
print("Working directory is ",os.getcwd())

BUILD_DICTs = True   # set to True to rebuild dictionaries

#ff_fileName =  "csvFiles/utmTest.csv"  Note Bene  file name is stored in globalParameters.py
#  Note Bene:  Make sure whale file has been sorted by year, mo, day, hr, min, sec and is TAB delimited

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

#################################Helpers
def unique(list1): 
  # insert the list to the set 
  list_set = set(list1) 
  # convert the set to the list 
  return list(list_set) 
##########################################

nfwf_ff_file=open(gp.ff_fileName, encoding="latin-1")
data = nfwf_ff_file.readline()[:-2].split('\t')   # read header data line
print("whale header items \n",data)

# dictionaries
anonBoatsDict = {}
codeCountDict = {}
boatsDict = {}
activityCodeDict = {}
oneTimeDict = {}

priorDataLine = ''

#############################################################################
def loadAllBoats(jdays):
  allBoatlines = []
  priorDataLine = ''
  with open(gp.boatFileName, encoding="latin-1") as boatFile:
    line = boatFile.readline()
    print("Boat Header\n",line)
    line = boatFile.readline()
    for line in boatFile:
      if line != priorDataLine:    #  this skips a line if it happens to be exactly equal to the prior data line
        priorDataLine = line
        items = line.split('\t')
        jday = WhaleBoatObj.getJulianDay(1,items)
        jdays.append(jday)
        allBoatlines.append(line)
  return allBoatlines

def buildDictionaries(allBoatLines):   # anonBoatsDict has link from BoatID_boatCode to all details abt this specific vessel
  global activityCodeDict
  for line in allBoatLines:            #  anonBoatsDict.get('pcdist_BARGE')
    items = line.split("\t")           #  ('BARGE_3', 'Barge', 'VTUG', 'Mark on the barge the tug was pulling')
                                                         #this last field is specific to the specific vessel
    boatID = "%s_%s" % (items[8], items[9])  # BARGE_3 will be working id of this vessel
    boatCode = items[9]                      #   boatsDict.get('BARGE')
    codeDef = items[10]                      #   ('Barge', 'VTUG')     VTUG will be for the JASCO source levels
    jascoType = items[11]
    commBoatName = items[20]
    
#    print(boatID, boatCode, codeDef, jascoType, commBoatName)
    # see if boatID is already in dictionaries
    dictVal = anonBoatsDict.get(boatID)
#    print("-----------", boatID, boatCode, dictVal)
    if dictVal is None:
      #build new dictionary entries
#      print("codeCountDict[boatCode]",codeCountDict.get(boatCode),boatCode)
      cnt = codeCountDict.get(boatCode)
      if cnt is None:
        codeCountDict[boatCode] = 1
        cnt = 1
      else:
        codeCountDict[boatCode] = codeCountDict[boatCode] + 1
        cnt = codeCountDict.get(boatCode)
      thisCode = "%s_%d" % (boatCode, cnt)   #  HERE IS THE CONSTRUCTION OF ANONIMIZED BOAT NAME
      rename = oneTimeDict.get(items[8])
      if rename is None:
        oneTimeDict[items[8]] = thisCode   # this dictionary will be used to rename boats to anonomized form 
      anonBoatsDict[thisCode]=(boatID, codeDef, jascoType, commBoatName)
      dictVal = boatsDict.get(boatCode)
      if dictVal is None:
        boatsDict[boatCode]=(codeDef, jascoType)

  activityCodeDict = {1: ('resting', '(deep rest, hanging, logging at the surface: whales do not progress through the water)'),\
                2: ('slow trav', '(whales progress through the water, although they may not make forward progress over ground)'),\
                3: ('moderate trav','( travel in which whales do not porpoise)'),\
                4: ('fast trav', '(includes porpoising)'),\
                5: ('dispersed trav', '(foraging in a directional manner)'),
                6: ('milling', '(feeding, pursuit of prey, involving changes in directions)'),\
                7: ('tactile', '(socializing that involves touching another whale, such as petting, rolling or nudging)'),\
                8: ('display', '(socializing that does not involve touching, but may include spyhops, tail-lobs and breaches)'),\
                9: ('kelping object play', '(note when kelping also involves tactile interaction count it as tactile, rather than object play)')}


  #now need to apply anonimized name to the boat objects
      
#  print("anonBoatsDict",anonBoatsDict,"\n")
#  print("codeCountDict",codeCountDict,"\n")
#  input("rrrr")
#  print("boatsDict",boatsDict)
#  input("kkk")
        
def addLine(lineCnt, focalID, line, IDsList, linesLists):
  idx = 0
  if lineCnt > 9999:
    print("lineCnt",lineCnt, line)
    print("len linesList", len(linesLists))
#    input("in addLine")
  if focalID not in IDsList:    # idx will point to where the new line should be appended
    IDsList.append(focalID)
    idx = len(IDsList)
    if lineCnt > 9999:
      print("id not in list", focalID, IDsList)
  else:
    idx = IDsList.index(focalID)
    if lineCnt > 9999:
      print("id in list", focalID, IDsList, idx)
  newList = []
  newList.append(line)  
  if len(linesLists) < idx or len(linesLists) == 0:
    linesLists.append(newList)
  else:
    linesLists[idx].append(line)

#  print(linesLists)
#  print(len(linesLists[0]),IDsList)
  
  return
        
def scanForNextTimeGap(maxObsGapMins, gapList):   # Note Bene  do I have to check for too large a jump in X or Y, say from North to South or
  linesLists = []                                 # or some sort of measurement error?????
  IDsList = []
  foundTimeGap = False
  jdayPrior = -1
  
  lineCnt = 0
  priorDataLine = 'init'
  while not foundTimeGap:
    filePos = nfwf_ff_file.tell() # save file pointer so we can back up ONE LINE when passby has ended
    line = nfwf_ff_file.readline()
    if line == '':
      return linesLists
    if line != priorDataLine:   #  this skips a line if it happens to be exactly equal to the prior data line
      priorDataLine = line
      lineCnt += 1
      if len(line) == 0:
        break            # reached end of data file
      items = line.split("\t")
      jday = WhaleBoatObj.getJulianDay(0,items)  

      focalID = items[7] # focal animal for this data file line
      
      if jdayPrior > 0 and (jday - jdayPrior)*24*60  >= maxObsGapMins:  # a passby has surely ended
        foundTimeGap = True
        nfwf_ff_file.seek(filePos)  # move file pointer back on line in data file
        gapList.append((jday - jdayPrior)*24*60)
  #      input("???????")
      else:
        addLine(lineCnt, focalID, line, IDsList, linesLists)    # THIS IS A COMPLICATED FUNCTION THAT BUILDS LISTS OF LISTS
  
      jdayPrior = jday  
  return linesLists

def getBoats(passbyCnt, jDayStart, jDayStop, priorOrPostMin):  # boatsJdays is a list of the ys for each line in boat file
  boatsObjList = []  
  boat_IDs = []
  dt = priorOrPostMin/(60*24)  # fraction of a day
  if jDayStop < jDayStart or jDayStop > boatsJdays[-1]:
    return boatsObjList
  idxStart = 0
  while boatsJdays[idxStart] < jDayStart - dt:
    f = open(gp.theoTracks_2019_FileName,'r')
    print(f.readline())
#    print(boatsJdays[idxStart] , jDayStart, idxStart, dt)
#    input("oo")
    idxStart += 1
  idxStop = idxStart
  while boatsJdays[idxStop] < jDayStop + dt:
    idxStop += 1
  boats = []  
  for i in range(idxStart,idxStop):
    boats.append(allBoatLines[i])  
  # boats has the data lines for each boat that was observed during this whale passby  
    items = allBoatLines[i].split('\t')
    boat_IDs.append(items[8])
  uniqueBoats = unique(boat_IDs)  
#  print("unique boats", uniqueBoats)
#  print(boat_IDs)
#  input("yyyyy)")
  for boatID in uniqueBoats:
    b_lines=[]
    for b in boats:   # run over all the boat lines for this passby
      items = b.split('\t')
      if items[8] == boatID:
        b_lines.append(b)  # this is a list of all the obs for a specific boat during this passby
    thisID = boatID.split('_')  # anonimized ID will split while raw one will not
    if len(thisID) == 1:
      thisID = oneTimeDict[boatID]  #  HERE WE ANONIMIZE THE BOAT ID if it has not already been done

    thisBoatsObs = WhaleBoatObj.boatObs(passbyCnt, thisID, b_lines)
    boatsObjList.append(thisBoatsObs)
#  print("leaving getBoats with list of length",len(boatsObjList),"idxStart=",idxStart,"idxStop=",idxStop)
  return boatsObjList


def writeErrorToFile(dataFileName, lineNo, errTxt):
  outputFile = []
  if not path.exists(parseErrorFileName):
    header = "Errors found in parsing NFWF file\n"
    outputFile = open(parseErrorFileName, 'w+')
    outputFile.write(header)
  else:
    outputFile = open(parseErrorFileName, 'a')
  print("file", dataFileName, "lineNo", lineNo,  "Error is", errTxt)
  
  line = "file %s line %d :: %s\n" % (dataFileName, lineNo, errTxt)
  
  outputFile.write(line)
  outputFile.close()

def logPassbyLists(theLists):
  print("in logPassbyLists with N lists=",len(theLists))
  i = 0
  for lst in theLists:
    i += 1
    items = lst[0].split("\t")
    focus = items[7]
    startDT = "%s_%s_%s_%s_%s_%s" % (items[0],items[2],items[3],items[4],items[5],items[6])
    items = lst[-1].split("\t")
    stopDT  = "%s_%s_%s_%s_%s_%s" % (items[0],items[2],items[3],items[4],items[5],items[6])

    logdata = "# in group %d \twhale = %s \tStart = %s \tStop = %s\n" % (i,focus,startDT,stopDT)
    logFile.write(logdata)
    print("logdata=",logdata)
    
def save_CVS_format(whalePassbyList, boatsPassbyList):
  #  write out tab delimited text file for all the whale data
  debug = 0
  whaleFile = open(gp.whaleCVSfileName,"w")
  header = "classtype\ttrackID\ttrackIDroberin\tsite\twhaleID\tage\tyear\tmonth\tday\thr\tminute\tsec\tjDay\twCalf\tactivityCode\tActivityState\tXroberin\tYroberin\tlatitude\tlongitude\tutmE\tutmN\tvE\tvN\tv\ta\ttortuosity\n"
  whaleFile.write(header)
  for w in whalePassbyList:
    fileline = "%s\t%d\t%d\t%s\t%s\t%d" % (w.classType, w.trackID, w.trackIDroberin,w.site,w.whaleID,w.age)
    for i in range(w.Nobs):
      theDate = helpers.getDate(w.jDay[i])
      fileline2 = "\t%d\t%d\t%d\t%d\t%d\t%d\t%0.7f\t%s\t%d\t%s\t%d\t%d\t%0.6f\t%0.6f\t%d\t%d" % (theDate[0],theDate[1],theDate[2],theDate[3],theDate[4],theDate[5],w.jDay[i],helpers.bytes2str(w.wCalf[i]), w.activityCode[i], helpers.bytes2str(w.activityState[i]), w.Xroberin[i],w.Yroberin[i],w.latitude[i],w.longitude[i],w.utmE[i],w.utmN[i])    
      fileline3 ="\t%0.3f\t%0.3f\t%0.3f\t%0.3f\t%0.3f\n" % (w.vE[i],w.vN[i],w.v[i],w.a[i],w.tortuosity[i])  
                 
      whaleFile.write(fileline + fileline2 + fileline3)
    if debug == 1:
      debug = 0
#      input("kkkk")
  whaleFile.close()

  boatFile = open(gp.boatCVSfileName,"w")
  header = "classtype\ttrackID\ttrackIDroberin\tsite\tboatID\tboatCode\tboatCodeDefinition\tJASCO_boatType\tyear\tmonth\tday\thr\tminute\tsec\tjDay\tXroberin\tYroberin\tlatitude\tlongitude\tutmE\tutmN\tvE\tvN\tv\ta\ttortuosity\\n"
  boatFile.write(header)
  for boats in boatsPassbyList:  # each entry is a LIST of boat observations in current passby
    for b in boats:
      fileline = "%s\t%d\t%d\t%s\t%s\t%s\t%s\t%s" % (b.classType,b.trackID, b.trackIDroberin,b.site,b.boatID,b.boatCode,b.boatDefinition,b.JASCOcode)
      for i in range(b.Nobs):
        theDate = helpers.getDate(b.jDay[i])

        fileline2 = "\t%d\t%d\t%d\t%d\t%d\t%d\t%0.7f\t%d\t%d\t%0.6f\t%0.6f\t%d\t%d" % (theDate[0],theDate[1],theDate[2],theDate[3],theDate[4],theDate[5], b.jDay[i], b.Xroberin[i],b.Yroberin[i],b.latitude[i],b.longitude[i],b.utmE[i],b.utmN[i])  
        fileline3 ="\t%0.3f\t%0.3f\t%0.3f\t%0.3f\t%0.3f\n" % (b.vE[i],b.vN[i],b.v[i],b.a[i],b.tortuosity[i])                                  
        boatFile.write(fileline + fileline2 + fileline3) 
  boatFile.close()
  
##############################  condense obs that are to close together in time
      
      ## go through allPassbys and find successive jDays that are closer together than parameter gp.condenseIfDtLessThan

def scanPassbyList(passbys):
  #  average any pairs of obs (obs that are very close in time)
  # gp.condenseIfDtLessThan = minimum time allowable between successive observations in sec
  cnt = 0
  sec2hr = 1/(24*3600)
  for passby in passbys:
#    print("passby=",passby)
    whale = passby[0]
    boats = passby[1]
    for boat in boats:  #  this is either a whale object or a boat object
#      print("target=",target)
      priorJday = boat.jDay[0]
      idx99 = []
      for i in range(1,len(boat.jDay)):
        thisJday = boat.jDay[i]
        if abs(thisJday - priorJday) < gp.condenseIfDtLessThan * sec2hr:
          cnt += 1
          print(cnt,"TrackID",boat.trackIDroberin,boat.trackID,"delta t (sec) =",int((thisJday - priorJday)/sec2hr),helpers.getDate(priorJday),helpers.getDate(thisJday))
          # here we average the thisJday and priorJday obs and mark one's utm's as -99  i.e.  Not and good
          boat.utmE[i] = (boat.utmE[i] + boat.utmE[i-1])/2.0
          boat.utmN[i] = (boat.utmN[i] + boat.utmN[i-1])/2.0
          boat.utmE[i-1] = -99           
          boat.utmN[i-1] = -99 # temp markers  -- not used but for debugging
          idx99.append(i-1)
        priorJday = thisJday     
      # now condense out the -99 records  
      if idx99 != []:
        boat.jDay = np.delete(boat.jDay,idx99)
        boat.Xroberin = np.delete(boat.Xroberin,idx99)
        boat.Yroberin = np.delete(boat.Yroberin,idx99)
        boat.utmE = np.delete(boat.utmE,idx99)
        boat.utmN = np.delete(boat.utmN,idx99)
        boat.vE = np.delete(boat.vE,idx99)
        boat.vN = np.delete(boat.vN,idx99)
        boat.a = np.delete(boat.a,idx99)
        boat.v = np.delete(boat.v,idx99)
        boat.tortuosity = np.delete(boat.tortuosity,idx99)
        boat.latitude = np.delete(boat.latitude,idx99)
        boat.longitude = np.delete(boat.longitude,idx99)
        boat.Nobs = len(boat.jDay)
      boat.smoothKinematics()

      
#########################################################################################  Program execution starts here
  #######################################################################################
boatsJdays = []
allBoatLines = loadAllBoats(boatsJdays)   #boatsJdays is a 1-D array with the julian time for each line in boat file
logFile = open(parserLogFileName, 'w')
if BUILD_DICTs:
  buildDictionaries(allBoatLines)
  helpers.save_obj(anonBoatsDict,"anonimizer")
  helpers.save_obj(boatsDict,"boats")
  helpers.save_obj(codeCountDict, "counts")
  helpers.save_obj(activityCodeDict,"activityCode")

else:
  anonBoatsDict = helpers.load_obj("anonimizer")
  boatsDict = helpers.load_obj("boats")
  codeCountDict = helpers.load_obj("counts")
  activityCodeDict = helpers.load_obj("activityCode")

passbyLinesLists = ['init']
passbyCnt = 0
whalePassbyList = []
boatsPassbyList = []
tracksList = []
gapList = []    # list of gaps identified between passby (in minutes)
lineCnt = 0
while len(passbyLinesLists) > 0:
  
  passbyLinesLists = scanForNextTimeGap(gp.maxObsGapMins, gapList)   # scans data input puting lines into passbyLinesLists according
  logPassbyLists(passbyLinesLists)                                   # to whaleID which is put into passbyIDsList
  for thisWhalePassbyLines in passbyLinesLists:  # run through the list of passby lists returned from scaning data file
    if len(thisWhalePassbyLines) > 0: 
      print("passbyCnt=",passbyCnt,"Nlines =",len(thisWhalePassbyLines))
      lineCnt += len(thisWhalePassbyLines)
      if len(thisWhalePassbyLines) < gp.minNumWhaleObs:
        nLines = len(thisWhalePassbyLines)
        errTxt = "Short passby, # lines= %d\n%s " % (nLines, thisWhalePassbyLines)
        writeErrorToFile('Whales', lineCnt, errTxt)
        print(errTxt)
      else:
        thisWhale = WhaleBoatObj.whaleObs(passbyCnt, thisWhalePassbyLines)
        print("line N=",lineCnt, "passby N=", passbyCnt,"animal",thisWhale.whaleID, "passby start stop",WhaleBoatObj.getDateFromJulian(thisWhale.jDay[0]), WhaleBoatObj.getDateFromJulian(thisWhale.jDay[-1])) 
        
        thisPassbysBoats = getBoats(passbyCnt, thisWhale.jDay[0], thisWhale.jDay[-1], gp.maxPriorOrPostMinsForBoats)
        #thisPassbysBoats a list of all the boats observed while thisWhale was passing
  
        if len(thisPassbysBoats) > 0:
          print(passbyCnt, thisWhale.trackID, thisPassbysBoats[0].trackID)
          thisWhale.nBoats = len(thisPassbysBoats)
          nMoving = 0
          for boat in thisPassbysBoats:
            if boat.Nobs > 1:
              nMoving += 1
          thisWhale.nBoatsMoving = nMoving    
        else:
          print(passbyCnt, thisWhale.trackID,"NO BOATS")
#        input("??????")
        passbyCnt += 1
      
        whalePassbyList.append(thisWhale)
        boatsPassbyList.append(thisPassbysBoats)  # this is a list of all of the lists of boats in all of the passbys
        track = [thisWhale, thisPassbysBoats]
        tracksList.append(track)
#        print(thisWhale.trackID)
#        input(">>>>>>")
#      if passbyCnt >= 10:
#        break
  
  #    print(boatsPassbyList)  
  #    input("??????")
#print("List of detected gaps")
#for dt in gapList:
#  print(int(dt))
#helpers.scanPassbyList(boatsPassbyList)    ##  scan list for errors  e.g.  to obs too close together

logFile.close()  
scanPassbyList(tracksList)   # this is a scan to remove obs that are too close together and then smooth the kinematics  ?? Boats only??
whalePassbyList = []
boatPassbyList  = []
for track in tracksList:
  whalePassbyList.append(track[0])
  boatPassbyList.append(track[1])


save_CVS_format(whalePassbyList, boatsPassbyList)
helpers.save_obj(whalePassbyList,"whalePassbys_2003_2005")  
helpers.save_obj(boatsPassbyList,"boatsPassbys_2003_2005")
helpers.save_obj(tracksList,"tracksList_2003_2005")

#wobs = whalePassbyList[0]
#print(wobs.classType, wobs.Nobs, wobs.trackID,  wobs.whaleID, wobs.trackIDroberin)
#print(wobs)  
  #thisWhalePassby = []   # used to stop the looping while debugging
  

