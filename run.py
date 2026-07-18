from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import json
import os
import schedule
import time
from dotenv import load_dotenv

from cineplex import regularEmail, availableShowtimes, movieTitle, writeToAvail, reset, checkShowtime, \
    scrapeShowtimeIDs, insertTheatre, movieTheatres, movieDates, insertDate, filters, insertMovie, start, options, \
    filterList, setAvailableJSON, driver, options
from urllib3.exceptions import MaxRetryError
import threading
from helper import theatresDict as theatres, seatTypes

#options = Options()
#options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
#driver = webdriver.Chrome(options=options)
load_dotenv()
script_dir = os.path.dirname(os.path.abspath(__file__))
wait = WebDriverWait(driver, 20)
with open(os.path.join(script_dir, "form_data.json"), "r") as openFile:
    data = json.load(openFile)


'''exclSeat = ["F", "G", "H", "I", "J"]
times = []
excludeTimes = ["11:00 AM", "2:30 PM", "10:30 PM"]
specExcludeSeat = []
for i in range(1, 9):
    for seat in exclSeat:
        specExcludeSeat.append(seat+str(36-i))
        specExcludeSeat.append(seat+str(i))
#print(excludeSeat)
showFailure = False

key = "realdynedl@gmail.com"
entry = 0

movieTitle = data[key][entry]["movie"]
movieTheatres = data[key][entry]["theatreID"]
movieDates = data[key][entry]["date"]
filterList = data[key][entry]["filter"]
excludeType = data[key][entry]["excludeSeatType"]
excludeSeat = data[key][entry]["excludeSeat"]
recipients = data[key][entry]["recipients"]'''

showtimeIDs = []
availableShowtimes = []
#availableJSON = []


driverAlive = True
run_lock = threading.Lock()
def run():
    global wait, driverAlive, driver
    if not run_lock.acquire(blocking=False):
        print("Previous run still in progress, skipping this cycle")
        return
    try:
        if not driverAlive:
            #driver = webdriver.Chrome()
            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver, 20)
            driverAlive = True
        start()

        insertMovie(movieTitle)
        if len(filterList) != 0:
            filters()
        for date in movieDates:
            insertDate(date)
            for theatre in movieTheatres:
                insertTheatre(theatres[theatre], int(theatre))
                showtimeIDs = scrapeShowtimeIDs()
                print(showtimeIDs)
                if len(showtimeIDs) == 0:
                    quit("No showtime exists for "+movieTitle, "Hang on tight! Hopefully more showtimes will arrive for " +movieTitle+".")
                    return
                    #writeToAvail(False)
                else:
                    for showtime in showtimeIDs:
                        print(f"\n\n{theatres[theatre]}")
                        checkShowtime(int(theatre), showtime)
        if len(availableShowtimes) == 0:
            setAvailableJSON(["No available seats for "+movieTitle, "Hang on tight! Hopefully more seats will arrive for " +movieTitle+"."])
            writeToAvail(False)
        elif len(availableShowtimes) == 1:
            setAvailableJSON(["There is 1 available seat for " + movieTitle, availableShowtimes])
            writeToAvail(True)
        else:
            setAvailableJSON(["There are " + str(len(availableShowtimes))+ " available seats for " + movieTitle, availableShowtimes])
            writeToAvail(True)
        reset()
    except TimeoutException as e:
        print(f"Timed out during run(): {e}")

    except MaxRetryError as e:
        print(f"Max retry error during run(): {e}")

    finally:
        run_lock.release()


schedule.every(5).seconds.do(run)
schedule.every(20).minutes.do(regularEmail)
while True:
    schedule.run_pending()
    time.sleep(1)