# BPCodeComp

My submission for @bp22's coding contest

interactive graph: https://htmlpreview.github.io/?https://github.com/AlexMusk/BPCodeComp/blob/main/webview.html


Main Decision Points:

First Check the data is as I expect it to be:
- Do any cities have multiple weather stations?

  yes: Portland: {'KPWM', 'KPDX'}
  
  solution: take the average temperature between the two weather stations and use that as one single value for portland
  
- Do any cities report multiple times in one day?

  no
  
- Do all of the reported temperatures have population data?

  no: {'NYC/LaGuardia', 'Windsor Locks', 'Covington', 'Wash DC/Dulles', 'Phoenix/Sky HRBR', 'Detroit/Wayne', "Chicago O'Hare", 'St Louis/Lambert', 'Sacramento/Execu', 'Raleigh/Durham', 'Albany'}
  all report data but do not have a population count to lookup
  
  solution: ignore them - I hope it's not a cop out but the brief did specify "using only this data"
  
Dealing with missing data:
- scan for dates with no data then fill in with the average of values at the closest before data and closes after data ( (a+b)/2 )
 
  could come up with a more complex solution for spans of 2+ days without data but since this does not appear in the sample it seems redundant
  
  if an item is at the end of the data (very first or very last day) it uses the closes available day in the other direction
