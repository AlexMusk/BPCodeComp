
# BPCodeComp

### My submission for @bp22's coding contest

__Interactive Graph:__ https://htmlpreview.github.io/?https://github.com/AlexMusk/BPCodeComp/blob/main/webview.html

__Cities/Stations Map:__ https://htmlpreview.github.io/?https://github.com/AlexMusk/BPCodeComp/blob/main/mapview.html

__Dependancies:__
* plotly (https://plotly.com/python/getting-started/)
* haversine (https://pypi.org/project/haversine/)

## Main Decision Points:
### First Check the data is as I expect it to be:
* __Do any cities have multiple weather stations?__
  * _Yes:_ Portland: {'KPWM', 'KPDX'} and Washington: {'KDCA', 'KIAD'}
  * _Solution:_ take the average temperature between the two weather stations and use that as one single value for Portland/Washington
 
* __Do any cities report multiple times in one day?__
  * _No_

* __Do all of the reported temperatures have population data?__
  * _No:_ {'NYC/LaGuardia', 'Windsor Locks', 'Covington', 'Wash DC/Dulles', 'Phoenix/Sky HRBR', 'Detroit/Wayne', "Chicago O'Hare", 'St Louis/Lambert', 'Sacramento/Execu', 'Raleigh/Durham', 'Albany'}
  * all report data but do not have a population count to lookup
  * <s>_Solution:_ ignore them - I hope it's not a cop out but the brief did specify "using only this data"</s>
  * _Solution:_ Manually map the data to the closes weather station. Method explained in comments at the top of 'GenerateGraphs.py'

### Dealing with missing data:
* Scan for dates with no data then fill in with the average of values at the previous date and closest following date ( (a+b)/2 )
* could come up with a more complex solution for spans of 2+ days without data but since this Does not appear in the sample it seems redundant
* If an item is at the end of the data (very first or very last day) it uses the closest available day in the other direction

### Calculating the weighted average:

* The weighted average is the sum of the temperatures from each population zone multiplied by their population then divided by the total population <s>(IMPORTANT: totalPop is only taken from the cities we actually use)</s> _(I now use all population data)_

### Potential Improvements:
* In this version I take the population zone's temperature to be the weather station with the same name or the weather station whose name is geographically closest the the zone.
* Using exact coordinates of each station it might be possible to average available temperature data to estimate the temperature at the exact lat/lon of the population zone's center.
* Accuracy could also obviously be improved by using more weather station data, which seems to be publicly available.

##### footnotes: learn chinese so I never get 'date' and 'data' mixed up again :)