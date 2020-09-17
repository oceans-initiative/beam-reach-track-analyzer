#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 5:26:24 2020

@author: val
"""
from jdcal import gcal2jd, jd2gcal
import pickle as pickle
import os
from os import path

os.chdir("/home/val/Documents/NFWF_Files/2020_Analysis/")
print("Working directory is ", os.getcwd())


##########################################################  helper functions
def bytes2str(data):
    return "".join(chr(x) for x in data)


def getDate(jDay):
    jd = (2400000.5, jDay)  # Note:  This is a tuple, not a list (i.e. ordered and unchangeable)
    dt = jd2gcal(*jd)
    yr = dt[0]
    mo = dt[1]
    day = int(dt[2])
    dayFrac = dt[3]
    hr = int(dayFrac * 24)
    mins = int((dayFrac * 24 - hr) * 60)
    sec = round((dayFrac * 24 - hr - mins / 60) * 3600)
    return (yr, mo, day, hr, mins, sec)


def save_obj(obj, name):
    with open('obj/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    print("Working directory is ", os.getcwd())
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def printPassby(w, bs, outputFileName):
    outputFile = []
    if not path.exists(outputFileName):
        header = "jdatetime\ttrack_ID\tfocalAnimal\tutmE\tutmN\tvE\tvN\taE\taN\ttau\tRL\tdComm\tdForage\n"
        outputFile = open(outputFileName, 'w+')
    ####    outputFile.write(header)
    else:
        outputFile = open(outputFileName, 'a')
    #  print("N boats is",len(bs))
    header = "WorB\tID\tutmE\tutmN\n"
    outputFile.write(header)

    for i in range(len(w.tModSecs)):
        dataline = "W\t%s\t%d\t%d\n" % (w.whaleID, w.xMod[i], w.yMod[i])
        outputFile.write(dataline)
    #  for b in bs:
    #    print("b len=",len(b.tModSecs))
    #    for i in range(len(b.tModSecs)):
    #      dataline = "B\t%s\t%d\t%d\n" % (b.boatID, b.xMod[i], b.yMod[i])
    #      outputFile.write(dataline)
    #    for i in range(0,len(w.xMod),max(1,int(len(w.xMod)/50))):
    #      print(i,w.whaleID,w.xMod[i], w.yMod[i],b.boatID, b.xMod[i], b.yMod[i],b.rWhale[i], b.bearingWhale[i])
    outputFile.close()


def scanPassbyList(passbys):
    #  average any pairs of obs (obs that are very close in time)
    minObservationDelta = 60  # minimum time allowable between successive observations in sec
    sec2hr = 1 / (24 * 3600)
    for passby in passbys:
        priorJday = passby.jDay[0]
        for i in range(1, len(passby.jDay)):
            thisJday = passby.jDay[i]
            if thisJday - priorJday < minObservationDelta * sec2hr:
                print("Observations too close at ", passby[1].trackID, thisJday, priorJday,
                      (thisJday - priorJday) / sec2hr)
            priorJday = thisJday


def loadDictionaries():
    anonBoatsDict = load_obj("anonimizer")
    boatsDict = load_obj("boats")
    codeCountDict = load_obj("counts")
    behaviorDict = load_obj("behavior")
    jascoCodesDict = load_obj("jascoCodes")
    echoSL_Dict = load_obj("echoSL")


def buildJascoCodeDict():
    #############  get all boat codes
    allPassbys = load_obj("tracksModel_2003_2005")  # this is list of passbys where each passby is one whale object
    boatCodes = []
    jascoCodes = []
    jascoCodeDict = {}
    for passby in allPassbys:
        boats = passby[1]
        for boat in boats:
            boatCode = boat.boatCode
            if boatCode not in boatCodes:
                boatCodes.append(boatCode)
            if boat.JASCOcode not in jascoCodes:
                jascoCodes.append(boat.JASCOcode)

            if not boat.JASCOcode in jascoCodeDict:
                jascoCodeDict[boat.JASCOcode] = [boatCode]
            else:
                if not boatCode in jascoCodeDict[boat.JASCOcode]:
                    jascoCodeDict[boat.JASCOcode] = jascoCodeDict[boat.JASCOcode] + [boatCode]

    print(boatCodes)
    print(jascoCodes)
    print(jascoCodeDict)

    for key in jascoCodeDict:
        print(key, ":", jascoCodeDict[key])
    save_obj(jascoCodeDict, "jascoCodes")

def asInt(x):
  try:
    return int(x)
  except:
    return -999999

def getJulianDay(offset,
                 items):  # items are year, anything, month, day, hour, minute, second  with offset=1 for boat file
    jd = gcal2jd(asInt(items[offset + 0]), asInt(items[offset + 2]), asInt(items[offset + 3]))[1] + (
            asInt(items[offset + 4]) + asInt(items[offset + 5]) / 60 + asInt(items[offset + 6]) / 3600) / 24.0
    return jd


def getJulianDayNew(yr, mo, dy, hr, mn,
                    sc):  # items are year, anything, month, day, hour, minute, second  with offset=1 for boat file
    jd = gcal2jd(asInt(yr), asInt(mo), asInt(dy))[1] + (asInt(hr) + asInt(mn) / 60 + asInt(sc) / 3600) / 24.0
    return jd


def getDateFromJulian(jDay):
    dt = jd2gcal(2400000.5, jDay)
    dayDec = dt[3] - int(dt[3])
    hr = int(dayDec * 24)
    minDec = dayDec - hr / 24
    minute = int(minDec * 60 * 24)
    sec = int((dayDec * 24 - hr - minute / 60) * 3600)
    return (dt[0], dt[1], dt[2], hr, minute, sec)


def getDateStrFromJulian(jDay):
    datetime = getDateFromJulian(jDay)
    #  return f"{datetime[0]}/{datetime[1]:02}/{datetime[2]:02} {datetime[3]:02}:{datetime[4]:02}:{datetime[5]:02}"  ## 2003/07/30 05:09:24
    formattedLine = f"{datetime[1]}/{datetime[1]}/{datetime[0]} {datetime[3]:02}:{datetime[4]:02}:{datetime[5]:02}"
#    print(formattedLine)
    return formattedLine  # 7/7/2003 05:09:24