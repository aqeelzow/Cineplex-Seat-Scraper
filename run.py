import os
from cineplex import runAll

#exclSeat = []
times = []
excludeTimes = [] #if there are specific showtimes you want to ignore (ex. '11:00AM'). might be bugged lowkey
specExcludeSeat = [] #if there are specific seats you want to ignore (ex. 'B5')
'''for i in range(1, 9):
    for seat in exclSeat:
        specExcludeSeat.append(seat+str(36-i))
        specExcludeSeat.append(seat+str(i))'''
#print(specExcludeSeat)


emailKey = "your_email@gmail.com"
emailEntry = 0
script_dir = os.path.dirname(os.path.abspath(__file__))
pathToFile = os.path.join(script_dir, "form_data.json")
pathToAvailJson = os.path.join(script_dir, "available.json")

runAll(pathToFile, emailKey, emailEntry, pathToAvailJson, specExcludeSeat, excludeTimes)
