'''
so since location data is included i probably should have realised it could be useful;
areas without a direct weather station are still some distance from a weather station so we can esimate their temperature by distance to the station
and this should give us a better population weighted average

            ----------------------

Decided that 'using only this data' means don't look for external temperature information and not that we can't lookup coordinates
so to improve the data we can manually map some names:

Chicago O'Hare -> Chicago
Detroit/Wayne -> Detroit
Phoenix/Sky HRBR -> Phoenix
Sacramento/Execu -> Sacramento
St Louis/Lambert -> St. Louis
Wash DC/Dulles -> Washington      (District Of Columbia)

Raleigh/Durham -> Raleigh
Raleigh and Durham both have populations and the station practically equidistant to both: choosing Raleigh

Albany
theres is nowhere close in our data set so ignoring for now. in a model where weather stations are not directly linked to cities we would use the coordinates below
[ 42.749111, -73.801972 ]
#https://forecast.weather.gov/MapClick.php?lat=42.7481&lon=-73.8023#.YNtshOhKi70

Windsor Locks -> Springfield
KBDL is 'Windsor Locks, Bradley International Airport, Connecticuit'
is actually geographically closest to Springfield Massachusetts

Covington -> Cincinnati
KCVG is 'Cincinnati/Northern Kentucky International Airport'
https://forecast.weather.gov/MapClick.php?lat=39.04456&lon=-84.67229#.YNtnJehKi70


NYC/LaGuardia -> New York? New York == New York City?
i'm not familiar with american geography but LaGuardia airport is in 'New York, New York' so this seems like a fine answer

for future reference:
   https://www.weather.gov/arh/stationlist
   http://www.weathergraphics.com/identifiers/
   has exact lat/lon locations for all weather stations

   but again not sure how strict 'only this data' is
'''

import csv
from datetime import datetime, timedelta
from collections import defaultdict
import plotly.graph_objects as go
import math
from haversine import haversine

ONE_DAY = timedelta(days=1)
US_DATE_FORMAT = "%m/%d/%Y"
UK_DATE_FORMAT = "%d/%m/%Y"

def dateStr(d):
   return d.strftime(US_DATE_FORMAT)

#City (0), Station Code (1), Date (2), Mean Temp (3), Min Temp (4), Max temp (5)
temperatureData = []

allNames = []
allDates = []
stations = defaultdict(list)
dates = defaultdict(list)

nameReplacementLookup = {
   "Chicago O'Hare": "Chicago",
   "Detroit/Wayne": "Detroit",
   "Phoenix/Sky HRBR": "Phoenix",
   "Sacramento/Execu": "Sacramento",
   "St Louis/Lambert": "St. Louis",
   "Wash DC/Dulles": "Washington",
   "Raleigh/Durham": "Raleigh",
   "Windsor Locks": "Springfield",
   "Covington": "Cincinnati",
   "NYC/LaGuardia": "New York"
}

#get the replacement in the table or return the default (our input)
def getNameReplacement(oldName):
   return nameReplacementLookup.get(oldName, oldName)

with open('Temperature Data.csv', newline='') as csvfile:
   reader = csv.reader(csvfile)
   next(reader)
   for row in reader:
      name = getNameReplacement(row[0])
      #ignore albany as explained above
      if name != 'Albany':
         date = datetime.strptime(row[5], "%m/%d/%Y")
         data = [name, row[4], date] + list(map(float, row[6:]))
         temperatureData.append(data)
         allNames.append(name)
         allDates.append(date)
         stations[name].append(row[4])
         dates[date].append(row[4])

# Check for cities with multiple stations, there is one:
# Portland: {'KPWM', 'KPDX'}
#Washington: {'KDCA', 'KIAD'} in v2
for k, v in stations.items():
   uniqueStations = set(v)
   if len(uniqueStations) > 1:
      print(k + ": " + str(uniqueStations))

# Check if any cities reported twice in one day
# (they don't)
for k, v in dates.items():
   seen = {}
   dupes = []
   for x in v:
    if x not in seen:
        seen[x] = True
    else:
        if seen[x] == True:
            dupes.append(x)

   if len(dupes) > 0:
      print(dateStr(k) + ": " + str(dupes))

#city names of all the weather stations that submitted data
uniqueNames = sorted(set(allNames))
#first date to appear in the data
firstDay = min(allDates)
#last date to appear in the data
lastDay = max(allDates)
allDatesInRange = set([date.fromordinal(i) for i in range(firstDay.toordinal(), 1+lastDay.toordinal())])
orderedDates = sorted(list(map(lambda x: x.isoformat(), allDatesInRange)))

totalPop = 0
#City: State (0), population (1), (Lon, Lat) (2)
cityLookup = {}
allCityNames = []

with open('Population Data.csv', newline='') as csvfile:
   reader = csv.reader(csvfile)
   next(reader)
   for row in reader:
      city = row[0]
      allCityNames.append(city)
      pop = float(row[2])
      totalPop += pop
      lon = float(row[3]);
      lat = float(row[4]);
      cityLookup[city] = [ row[1], pop, (lat, lon) ]

print("Total Population: " + str(totalPop) + ", Cities: " + str(len(allCityNames)) + ", Weather Stations: " + str(len(uniqueNames)))

#get the date closest to (but in the past) to 'date'
#if the we reach the earliest date in lookup then get the closest date in the other direction
def getBefore(lookup, date):
   beforeDate = date-ONE_DAY
   while True:
      if beforeDate in lookup:
         return beforeDate
      else:
         beforeData = beforeData-ONE_DAY
         if beforeData < firstDay:
            return getAfter(lookup, date)

#get the date closest to (but in the future) to 'date'
#if the we reach the latest date in lookup then get the closest date in the other direction
def getAfter(lookup, date):
   nextDate = date+ONE_DAY
   while True:
      if nextDate in lookup:
         return nextDate
      else:
         nextDate = nextDate+ONE_DAY
         if nextDate > lastDay:
            return getBefore(lookup, date)

#list of all the data that was generated by me
healedData = []

#find all dates with no data and fill it in with the average of the before data and after data ( (a+b)/2 )
#could come up with a more complex algorithm for spans of 2+ days without data but since this does not appear in the sample I didn't
#if an item is at the end of the data (very first or very last day) it uses the closes available day in the other direction
def healData(data):
   justDates = set(map(lambda d: d[2], data))
   misses = list(allDatesInRange - justDates)

   if len(misses) > 0:
      dateLookup = { x[2]: x for x in data }

      for m in misses:
         beforeData = dateLookup[getBefore(dateLookup, m)]
         afterData = dateLookup[getAfter(dateLookup, m)]

         newData = [data[0][0], data[0][1], m, 
            (beforeData[3]+afterData[3])/2, 
            (beforeData[4]+afterData[4])/2, 
            (beforeData[5]+afterData[5])/2]
         data.append(newData)
         healedData.append(newData)
   return data

#if the tuple contains numbers return the average otherwise return first item of tuple
def avg(tuple):
   if type(tuple[0]) is float or type(tuple[0]) is int:
      return float(sum(tuple)/len(tuple))
   else:
      return tuple[0]

#data filtered for specific station
#City: [ [ City (0), Station Code (1), Date (2), Mean Temp (3), Min Temp (4), Max temp (5) ] ]
stationData = {}
'''
since portland has two measurements for only one population count
I will take the average of both measurements and add that to the weighted total only once
'''
KPWM = sorted(healData(list(filter(lambda x : x[1] == "KPWM", temperatureData))), key=(lambda x: x[2]))
KPDX = sorted(healData(list(filter(lambda x : x[1] == "KPDX", temperatureData))), key=(lambda x: x[2]))
stationData['Portland'] = [avg(item) for item in zip(KPWM, KPDX)]

#washington now has two stations after update
KIAD = sorted(healData(list(filter(lambda x : x[1] == "KIAD", temperatureData))), key=(lambda x: x[2]))
KDCA = sorted(healData(list(filter(lambda x : x[1] == "KDCA", temperatureData))), key=(lambda x: x[2]))
stationData['Washington'] = [avg(item) for item in zip(KIAD, KDCA)]

stationCoordinateLookup = {}

for stationName in uniqueNames:
   if stationName != 'Portland' and stationName != 'Washington':
      stationData[stationName] = healData(list(filter(lambda x : x[0] == stationName, temperatureData)))

   cityForStation = cityLookup[stationName]
   stationCoordinateLookup[cityForStation[2]] = stationName

totalAvg = defaultdict(float)
totalMin = defaultdict(float)
totalMax = defaultdict(float)

def doTemperature(cityName, stationName):
   weight = cityLookup[cityName][1]/totalPop
      
   for day in stationData[stationName]:
      totalAvg[day[2]] += day[3]*weight
      totalMin[day[2]] += day[4]*weight
      totalMax[day[2]] += day[5]*weight


allStationCoords = list(stationCoordinateLookup.keys())
#this is all very inefficient but I think list is small enough just to brute force distances

for city in allCityNames:
   #if city is already mapped to a station
   if city in uniqueNames:
      doTemperature(city, city)
   #else find the closest station and use it's values
   else:
      distances = sorted(map(lambda c : [c, haversine(c, cityLookup[city][2])], allStationCoords), key=lambda x : x[1])
      
      # just use closest value (could use N values then average for better accuracy?)
      # but direction is important so would mean finding the center of different groups then comparing those distances;
      # seems computationally expensive for something i've not researched, will look into it for version 3
      first = distances[0]
      closestStation = stationCoordinateLookup[first[0]]
      doTemperature(city, closestStation)

theDay = firstDay
monthAvg = defaultdict(float)
monthMin = defaultdict(float)
monthMax = defaultdict(float)
monthDates = defaultdict(list)
monthAbsMin = {}
monthAbsMax = {}

seasonAvg = defaultdict(float)
seasonMin = defaultdict(float)
seasonMax = defaultdict(float)
seasonDates = defaultdict(list)
seasonAbsMin = {}
seasonAbsMax = {}

while theDay <= lastDay:
   monthIndex = theDay.month + ((theDay.year-2015)*12)
   monthAvg[monthIndex] += totalAvg[theDay]
   monthMin[monthIndex] += totalMin[theDay]
   monthMax[monthIndex] += totalMax[theDay]
   monthAbsMin[monthIndex] = min(monthAbsMin.get(monthIndex, totalMin[theDay]), totalMin[theDay]);
   monthAbsMax[monthIndex] = max(monthAbsMax.get(monthIndex, totalMax[theDay]), totalMax[theDay]);
   monthDates[monthIndex].append(theDay)

   seasonIndex = math.floor((theDay.month+1)/3) + ((theDay.year-2015)*4)
   seasonAvg[seasonIndex] += totalAvg[theDay]
   seasonMin[seasonIndex] += totalMin[theDay]
   seasonMax[seasonIndex] += totalMax[theDay]
   seasonAbsMin[seasonIndex] = min(seasonAbsMin.get(seasonIndex, totalMin[theDay]), totalMin[theDay]);
   seasonAbsMax[seasonIndex] = max(seasonAbsMax.get(seasonIndex, totalMax[theDay]), totalMax[theDay]);
   seasonDates[seasonIndex].append(theDay)

   theDay += ONE_DAY

#map dates to list of weather station keys that didnt report that day
healedDatesLookup = defaultdict(list)

for d in healedData:
   healedDatesLookup[d[2]].append(d[1])

COLOR_SEPARATOR = "grey"
COLOR_MAX_LINE = "crimson"
COLOR_AVG_LINE = "orange"
COLOR_MIN_LINE = "skyblue"
COLOR_MAX = "firebrick"
COLOR_AVG = "chocolate"
COLOR_MIN = "blue"
COLOR_ABS_MAX = "darkred"
COLOR_ABS_MIN = "darkcyan"
COLOR_ERROR_LINE = "darkslategrey"
WIDTH_OF_TRACE = 1
WIDTH_OF_TRENDS = 2
WIDTH_OF_MAX = 2
WIDTH_OF_ERROR_BAR = 1
WIDTH_OF_SEPARATORS = 0.4
DATA_TAG_FORMAT = "%{y:.2f}°C"

fig = go.Figure()
buttons = []

def trends(averages, dates, label, color):
   count = 0

   for k, v in averages:
      days = dates[k]
      x= days
      y = [v/len(days)]*len(x)
      fig.add_trace(go.Scatter(dict(x=x, y=y, mode='lines', line_color=color, hovertemplate=DATA_TAG_FORMAT, showlegend=(count==0), name=label, visible=False, line=dict(width=WIDTH_OF_TRENDS))))
      count += 1
   return count

def trendsMax(averages, dates, label, color):
   count = 0

   for k, val in averages:
      days = dates[k]
      x= days
      y = [val]*len(x)
      fig.add_trace(go.Scatter(dict(x=x, y=y, mode='lines', line_color=color, hovertemplate=DATA_TAG_FORMAT, showlegend=(count==0), name=label, visible=False, line=dict(width=WIDTH_OF_MAX))))
      count += 1
   return count

def separatorLines(dates):
   output = []

   for days in dates.values():
      d2 = days[-1]+ONE_DAY
      output.append(dict(type="line", x0=d2.isoformat(), y0=-10, x1=d2.isoformat(), y1=40, line=dict(color=COLOR_SEPARATOR, width=WIDTH_OF_SEPARATORS)))
   return output;

lineCount = 3

for k,v in healedDatesLookup.items():
   v.sort()
   tag = "<b>Missing Station Data</b> (" + dateStr(k) + ")<br><span style='font-size: 9px;'>"
   count = 0
   if len(v) > 1:
      for i in range(len(v)-1):
         tag += v[i] + ", "
         if count%8==7: tag += "<br>"
         count += 1
   tag += v[-1] + "</span><extra></extra>"

   fig.add_trace(go.Scatter(x=[k,k], y=[-10, 40], mode='lines', line_color=COLOR_ERROR_LINE, showlegend=False, hovertemplate = tag, line=dict(width=WIDTH_OF_ERROR_BAR)))
   lineCount += 1

fig.add_trace(go.Scatter(x=orderedDates, y=[v for [k,v] in sorted(totalMax.items(), key=(lambda x: x[0]))], hovertemplate=DATA_TAG_FORMAT, mode='lines', line_color=COLOR_MAX_LINE, name="Max Temp (day)", line=dict(width=WIDTH_OF_TRACE)))
fig.add_trace(go.Scatter(x=orderedDates, y=[v for [k,v] in sorted(totalAvg.items(), key=(lambda x: x[0]))], hovertemplate=DATA_TAG_FORMAT, mode='lines', line_color=COLOR_AVG_LINE, name="Mean Temp (day)", line=dict(width=WIDTH_OF_TRACE)))
fig.add_trace(go.Scatter(x=orderedDates, y=[v for [k,v] in sorted(totalMin.items(), key=(lambda x: x[0]))], hovertemplate=DATA_TAG_FORMAT, mode='lines', line_color=COLOR_MIN_LINE, name="Min Temp (day)", line=dict(width=WIDTH_OF_TRACE)))

monthCount = trendsMax(monthAbsMax.items(), monthDates, "Monthly Peak", COLOR_ABS_MAX) \
   + trends(monthMax.items(), monthDates, "Max Average (Month)", COLOR_MAX) \
   + trends(monthAvg.items(), monthDates, "Mean Average (Month)", COLOR_AVG) \
   + trends(monthMin.items(), monthDates, "Min Average (Month)", COLOR_MIN) \
   + trendsMax(monthAbsMin.items(), monthDates, "Monthly Trough", COLOR_ABS_MIN)

seasonCount = trendsMax(seasonAbsMax.items(), seasonDates, "Seasonal Peak", COLOR_ABS_MAX) \
   + trends(seasonMax.items(), seasonDates, "Max Average (Season)", COLOR_MAX) \
   + trends(seasonAvg.items(), seasonDates, "Mean Average (Season)", COLOR_AVG) \
   + trends(seasonMin.items(), seasonDates, "Min Average (Season)", COLOR_MIN) \
   + trendsMax(seasonAbsMin.items(), seasonDates, "Seasonal Trough", COLOR_ABS_MIN)

buttons.append(dict(label = 'Show Monthly Averages', method = 'update',
args = [{'visible': [True]*lineCount + [True]*monthCount + [False]*seasonCount}]))
buttons.append(dict(label = 'Show Seasonal Averages', method = 'update',
args = [{'visible': [True]*lineCount + [False]*monthCount + [True]*seasonCount}]))
buttons.append(dict(label = 'Hide Averages', method = 'update',
args = [{'visible': [True]*lineCount + [False]*monthCount + [False]*seasonCount}]))

fig.update_xaxes(showspikes=True, spikecolor="grey", spikethickness=1, spikemode="across")

fig.update_layout(
   title="Average Temperatures (Population Weighted, USA) <span style='font-size: 12px'>Population sampled: " + "{:,.0f}".format(totalPop) + "</span>",
   xaxis_title="Date",
   yaxis_title="Temperature (°C)",
   legend_title="Legend",
   hovermode='x',
   hoverdistance=2,
   xaxis=dict(
      rangeselector=dict(
         buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year",  stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
         ])
      ),
      rangeslider=dict(
         visible=True
      ),
      type="date"
   ),
   updatemenus=[
      dict(type="buttons", buttons=buttons)
   ]
)

fig.show()
#fig.write_html("webview.html")