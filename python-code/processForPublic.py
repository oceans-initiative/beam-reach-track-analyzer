"""
    Sept 15, 2020
    Unpacked pickled intermediate data files and save as csv for public access

"""

import os.path
from typing import List

import helpers

os.chdir("/home/val/Documents/NFWF_Files/2020_Analysis/")
print("Working directory is ", os.getcwd())

allPassbys = helpers.load_obj("tracksModel_RLs_2003_2005")
# each passby of allPassbys is a whale, boat pair  whale=passby[ ][0]  boats=passby[ ][1]


def buildRangeToWhale(Ipassby):
    whale = allPassbys[Ipassby][0]
    print(whale)
    if whale.nBoats == 0:
        return 0,0,0,0,0,0,0,0,0,0,0
    boats = allPassbys[Ipassby][1]

    rWhale = []
    N100 = N400 = N1000 = N5000 = 0
    for boat in boats:
#        print(boat)
#        print("len(rWhale)", len(boat.rWhale))
        for R in boat.rWhale:
            rWhale.append(R)
            if R < 100:
                N100 += 1
            if R < 400:
                N400 += 1
            if R < 1000:
                N1000 += 1
            if R < 5000:
                N5000 += 1

    totalCnt = len(rWhale)
    fracUnder5000 = N5000/totalCnt
    fracUnder1000 = N1000 / totalCnt
    fracUnder400 = N400 / totalCnt
    fracUnder100 = N100 / totalCnt

#    print(f'N100={N100}, N400={N400}, N1000={N1000}, N5000={N5000}, totalCnt={totalCnt} fracUnder5000={fracUnder5000:.3f}, fracUnder1000={fracUnder1000:.3f}, fracUnder400={fracUnder400:.3f},fracUnder100={fracUnder100:.3f}')#    print("min distance to whale=", round(min(rWhale)))
#    print("max distance to whale=", round(max(rWhale)))
    return round(min(rWhale)), round(max(rWhale)), N100, N400, N1000, N5000, totalCnt, fracUnder100, fracUnder400, fracUnder1000, fracUnder5000

def findClosestPassby(passbys, time, date):
    gotWhale = False
    print(time)
    hour = 0
    minute = helpers.asInt(list(time)[-1]) + helpers.asInt(list(time)[-2]) * 10   # this to hack through OI time format which is hrmn without leading zeros -- Ughhhhhhh
    if len(list(time)) ==4:
        hour = helpers.asInt(list(time)[1]) + helpers.asInt(list(time)[0])*10
    if len(list(time)) == 3:
        hour = helpers.asInt(list(time)[0])
    items = date.split("/")
    print("OI date is", date, items)
    day = helpers.asInt(items[0])
    month = helpers.asInt(items[1])
    year  = helpers.asInt(items[2])
    OI_jday = helpers.getJulianDayNew(year, month, day,hour, minute, 0)
    print("----------------------",date, time, year, month, day, hour, minute, OI_jday)
    idx = 0
    while (not gotWhale) and (idx < len(passbys)):
        whale = passbys[idx][0]
        print(idx, whale.jDay[0])
        if not whale.jDay[0] <= OI_jday:
            gotWhale = False
#            break
        idx += 1

    priorDelta = abs(passbys[idx-1][0].jDay[0] - OI_jday)
    postDelta  = abs(whale.jDay[0] - OI_jday)
#    print(idx, passbys[idx-1][0], whale)
#    print(idx, "priorDelta", priorDelta, helpers.getDateStrFromJulian(passbys[idx-1][0].jDay[0]))
#    print("priorDelta", postDelta, helpers.getDateStrFromJulian(passbys[idx][0].jDay[0]))
    if priorDelta < postDelta:
        return passbys[idx-1], priorDelta*24*60   # return abs difference in minutes
    else:
        return passbys[idx], postDelta*24*60



###############################################################  execution starts here
whale = allPassbys[1][0]
datetime = helpers.getDateFromJulian(whale.jDay[0])
datestr  = helpers.getDateStrFromJulian(whale.jDay[0])
print(datetime)
##dateStr = f"{datetime[0]}/{datetime[1]:02}/{datetime[2]:02} {datetime[3]:02}:{datetime[4]:02}:{datetime[5]:02}"
print(datestr)

#buildRangeToWhale(0)

print(len(allPassbys))

header = "Passby\tJulianDay\tDate\tTimeStart\tTimeStop\tMinDistance\tMaxDistance\tN100\tN400\tN1000\tN5000\ttotalCnt\tfracUnder100\tfracUnder400\tfracUnder1000\tfracUnder5000\n"
histogramFile = "csvFiles/2003_2005_PassbyHistograms.csv"
f = open(histogramFile, 'w')
f.write(header)
for i in range(len(allPassbys)):
    whale = allPassbys[i][0]
    trackID = whale.trackID
    jDay = whale.jDay[0]
    print(i, trackID, jDay)
    dt_start = helpers.getDateStrFromJulian(whale.jDay[0]).split(' ')
    dt_stop  = helpers.getDateStrFromJulian(whale.jDay[-1]).split(' ')
    minD, maxD, N100, N400, N1000, N5000, totalCnt, fUnder100, fUnder400, fUnder1000, fUnder5000 = buildRangeToWhale(i)
    if minD != 0 and maxD != 0:
        fileline = f"{trackID}\t{jDay:.4f}\t{dt_start[0]}\t{dt_start[1]}\t{dt_stop[1]}\t{minD:.0f}\t{maxD:.0f}\t{N100}\t{N400}\t{N1000}\t{N5000}\t{totalCnt}\t{fUnder100:.2f}\t{fUnder400:.2f}\t{fUnder1000:.2f}\t{fUnder5000:.2f}\n"
        print(fileline)
        f.write(fileline)

f.close()