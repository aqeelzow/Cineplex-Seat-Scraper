from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
import json
import os
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
from emailSend import readInfo, sendEmail
from urllib3.exceptions import MaxRetryError
from selenium.webdriver.chrome.options import Options



# theatre id: name
theatres = {
    7408: "Cineplex Cinemas Vaughan",
    7420: "Cineplex Cinemas Mississauga Square One"
}

seatTypes = ["Wheelchair", "Standard", "Companion", "D-BOX*" ]



# Initialize the driver
#driver = webdriver.Chrome()
options = Options()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
driver = webdriver.Chrome(options=options)
load_dotenv()
script_dir = os.path.dirname(os.path.abspath(__file__))
wait = WebDriverWait(driver, 20)
with open(os.path.join(script_dir, "form_data.json"), "r") as openFile:
    data = json.load(openFile)

excludeType = ["Wheelchair", "Companion"]
excludeSeat = ["A", "B", "C"]
movieTitle = "The Odyssey"
showFailure = False

movieTheatres = data["theatre_id"]
filterList = data["filters"]
movieDates = data["dates"]
showtimeIDs = []
availableShowtimes = []
availableJSON = []


## Claude code
def safeClick(element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    try:
        element.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", element)

def writeToAvail(success):
    global availableJSON, showFailure
    availableJSON.append(datetime.now().strftime("%H:%M:%S"))
    with open(os.path.join(script_dir, "available.json"), "w") as writeFile:
        json.dump(availableJSON, writeFile)
    if showFailure and not success or success:
        processAndSendEmail()

def processAndSendEmail():
    global availableShowtimes
    info = readInfo()
    sendEmail("realdynedl@gmail.com", ["realdynedl@gmail.com"], info[1], info[0], os.getenv("GOOGLEPASS"))
    availableShowtimes = []

def regularEmail():
    sendEmail("realdynedl@gmail.com", ["realdynedl@gmail.com"], "Working: "+ datetime.now().strftime("%H:%M:%S"), "As of "+datetime.now().strftime("%B %d, %Y")+" at "+datetime.now().strftime("%H:%M:%S") + " the program is working on: "+movieTitle + " at "+", ".join(str(t) for t in movieTheatres) + " for " +", ".join(movieDates), os.getenv("GOOGLEPASS"))
    print("regular email sent")

def quit(subject, bodyText):
    global availableJSON, driverAlive
    availableJSON = [subject, bodyText]
    driver.quit()
    driverAlive = False
    writeToAvail(False)
def start():
    driver.get("https://www.cineplex.com/?openTM=true")
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#onetrust-accept-btn-handler")))
        safeClick(driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-handler"))
    except TimeoutException:
        pass
        print("passing timeout exception")
    ''' if the random pop up shows up where it doesnt work
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, "#onetrust-accept-btn-handler")
        if len(elements) > 0:
            driver.refresh()
    except TimeoutException:
        pass
        print("passing timeout exception")  
    '''
def insertMovie(movieTitle):
    buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".TicketModuleButton_button__gOEtJ"))) #buttons
    for button in buttons:
        if "select-movie" in button.get_attribute("data-testid"):
            wait.until(EC.element_to_be_clickable(button))
            safeClick(button)
            break
    movieTitles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".SelectMoviesDrawer_movieTitle__xUE23")))
    found = False
    for movie in movieTitles:
        if movieTitle in movie.text:
            print("\nmovie title found")
            wait.until(EC.element_to_be_clickable(movie))
            safeClick(movie)
            found = True
            break
    if not found:
        quit(movieTitle + " was not found.", "The movie does not exist.")

def insertDate(movieDate):
    buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".TicketModuleButton_button__gOEtJ"))) #buttons
    for button in buttons:
        if "select-date" in button.get_attribute("data-testid"):
            wait.until(EC.element_to_be_clickable(button))
            safeClick(button)
            break
    movieDates = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".SelectDateDrawer_dateContainer__UOXZm")))
    found = False
    for date in movieDates:
        if movieDate in date.text:
            print("\nmovie date found")
            wait.until(EC.element_to_be_clickable(date))
            safeClick(date)
            found = True
            break
    if not found:
        quit("No showtimes for " +movieTitle + " were found for "+movieDate+".", "The showtime does not exist.")


def insertTheatre(movieTheatre, theatreID):
    buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".TicketModuleButton_button__gOEtJ"))) #buttons
    for button in buttons:
        if "select-theatre" in button.get_attribute("data-testid"):
            wait.until(EC.element_to_be_clickable(button))
            safeClick(button)
            break
    searchBox = driver.find_element(By.CSS_SELECTOR, ".FilterInput_searchInput__Arrk_")
    searchBox.clear()
    searchBox.send_keys(movieTheatre)
    ## Claude code
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".LoadingAnimation_container__nRpj6")))
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".LoadingAnimation_container__nRpj6")))
    movieTheatres = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, f"[data-testid*='theatre-id-{theatreID}']")))
    found = False
    for theatre in movieTheatres:
        if movieTheatre in theatre.text:
            wait.until(EC.element_to_be_clickable(theatre))
            safeClick(theatre)
            print("\nmovie theatre found")
            found = True
            break
    if not found:
        quit(movieTheatre + " was not found.", "The theatre does not exist.")
def filters():
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ShowtimesContent_filterButton__biqZY")))
    safeClick(driver.find_element(By.CSS_SELECTOR, ".ShowtimesContent_filterButton__biqZY"))

    ## Claude code
    #wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".LoadingAnimation_container__nRpj6")))
    #wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".LoadingAnimation_container__nRpj6")))
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".Checkbox_hover-row__bVtwf")))
    time.sleep(1)
    movieFilters = driver.find_elements(By.CSS_SELECTOR, ".Checkbox_hover-row__bVtwf")
    #movieFilters = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".Checkbox_hover-row__bVtwf")))
    foundOne = False
    for filt in filterList:
        found = False
        for myfilter in movieFilters:
            if filt == myfilter.text:
                wait.until(EC.element_to_be_clickable(myfilter))
                safeClick(myfilter)
                print("\nmovie filters found")
                found = True
                foundOne = True
                break
        if not found:
            continue
    if not foundOne:
        quit("No filters were found.", "Your selected filter(s) do not exist.")
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".SelectFilterDrawer_fullWidth__q2yZQ")))
    safeClick(driver.find_element(By.CSS_SELECTOR, ".SelectFilterDrawer_fullWidth__q2yZQ"))


def scrapeShowtimeIDs():
    global showtimeIDs
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid*='showtime-cta-vistaId-']")))
    time.sleep(3)
    ids = []
    showtimes = driver.find_elements(By.CSS_SELECTOR, "[data-testid*='showtime-cta-vistaId-']")
    for showtime in showtimes:
        showID = showtime.get_attribute("data-testid")
        showIDfix = showID.replace("showtime-cta-vistaId-","")
        ids.append(showIDfix)
    return ids
## Claude code
def waitForSeatAvailability(minCalls, quietPeriod, timeout):
    global driver
    seenIDs = set()
    finishedIDs = set()
    lastActivity = time.time()
    startTime = time.time()

    while time.time() - startTime < timeout:
        for entry in driver.get_log("performance"):  # clears buffer each call
            try:
                msg = json.loads(entry["message"])["message"]
            except (KeyError, ValueError):
                continue

            method = msg.get("method")
            params = msg.get("params", {})

            if method == "Network.responseReceived":
                url = params.get("response", {}).get("url", "")
                if "seat-availability" in url:
                    seenIDs.add(params["requestId"])
                    lastActivity = time.time()

            elif method == "Network.loadingFinished":
                if params.get("requestId") in seenIDs:
                    finishedIDs.add(params["requestId"])
                    lastActivity = time.time()

        if len(finishedIDs) >= minCalls and (time.time() - lastActivity) > quietPeriod:
            return True

        time.sleep(0.1)

    return False  # timed out — fall back to whatever you had before
def checkShowtime(theatreID, showtimeID):
    #global availableJSON
    main_tab = driver.current_window_handle
    driver.switch_to.new_window('tab')
    url = f"https://www.cineplex.com/ticketing/preview?theatreId={theatreID}&showtimeId={showtimeID}&dbox=false"
    driver.get(url)

    # Locate a single element
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='seat-'] > g.SeatElement_seatLinkButton__wxQzX")))
    #time.sleep(1)
    #childElements = driver.find_elements(By.CSS_SELECTOR, "[class*='seat-'] > g.SeatElement_seatLinkButton__wxQzX")
    #allAvailable = True
    runDueToSeatMap = False
    '''shortWait = WebDriverWait(driver, 1)
    
    end_time = time.time() + 1.5
    prevViewBox = 0
    try:
        while time.time() < end_time:
            shortWait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".SeatMapSvg_preview__qA6DG")))
            renderedSeatMap = driver.find_element(By.CSS_SELECTOR, ".SeatMapSvg_preview__qA6DG")
            viewBox = driver.execute_script("return arguments[0].getAttribute('viewBox');", renderedSeatMap)
            if viewBox == prevViewBox and "1320 " not in viewBox:
                runDueToSeatMap = True
                break
            prevViewBox = viewBox
            time.sleep(0.1)
    except TimeoutException:
        print("Couldn't find non rendered seat map.")
        #viewBox = None
        runDueToSeatMap = True

    #if "1320 " not in renderedSeatMap.get_attribute("viewBox"):'''
    got_data = waitForSeatAvailability(2, 0.6, 8)
    if not got_data:
        print("Never saw seat-availability response — falling back to sleep")
        time.sleep(2)
    else:
        # tiny buffer for React to re-render aria-labels after the fetch resolves
        time.sleep(0.15)
        runDueToSeatMap = True
    childElements = driver.find_elements(By.CSS_SELECTOR, "[class*='seat-'] > g.SeatElement_seatLinkButton__wxQzX")
    if runDueToSeatMap:

        for element in childElements:
            exclude = False

            try:
                status = element.get_attribute("aria-label").casefold()
                #if "occupied".casefold() in status:
                    #allAvailable = False
                #elif "available" in status and not allAvailable:
                if "available" in status:
                    status = status.replace("available", "")
                    status = status.replace("seat", "")
                    for typeEx in excludeType:
                        if typeEx.casefold() in status.casefold():
                            exclude = True
                            status = status.replace(typeEx, "")
                    for seatType in seatTypes:
                        status = status.replace(seatType.casefold(), "")
                    for seatEx in excludeSeat:
                        if seatEx.casefold() in status.casefold():
                            exclude = True
                    if not exclude:
                        availableShowtimes.append(url + ":" + str(element.get_attribute("aria-label")))
                        print("added to availables")
                '''else:
                    availableJSON = ["No seats were found.", "That's odd, we couldn't find any seats."]
                    driver.quit()
                    writeToAvail()'''

                    #print(element.get_attribute("aria-label"))
            except StaleElementReferenceException:
                continue
    driver.close()
    driver.switch_to.window(main_tab)


def reset():
    closeTab = driver.current_window_handle
    driver.switch_to.new_window('tab')
    driver.get("https://www.cineplex.com/?openTM=true")
    mainTab = driver.current_window_handle
    driver.switch_to.window(closeTab)
    driver.close()
    driver.switch_to.window(mainTab)
driverAlive = True
def run():
    global availableJSON, wait, driverAlive, driver
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
                insertTheatre(theatres[theatre], theatre)
                showtimeIDs = scrapeShowtimeIDs()
                print(showtimeIDs)
                if len(showtimeIDs) == 0:
                    quit("No showtime exists for "+movieTitle, "Hang on tight! Hopefully more showtimes will arrive for " +movieTitle+".")
                    return
                    #writeToAvail(False)
                else:
                    for showtime in showtimeIDs:
                        print(f"\n\n{theatres[theatre]}")
                        checkShowtime(theatre, showtime)
        if len(availableShowtimes) == 0:
            availableJSON = ["No available seats for "+movieTitle, "Hang on tight! Hopefully more seats will arrive for " +movieTitle+"."]
            writeToAvail(False)
        else:
            availableJSON = ["There are " + str(len(availableShowtimes))+ " available seats for " + movieTitle, availableShowtimes]
            writeToAvail(True)
        reset()
    except TimeoutException as e:
        print(f"Timed out during run(): {e}")

    except MaxRetryError as e:
        print(f"Max retry error during run(): {e}")


schedule.every(5).seconds.do(run)
schedule.every(20).minutes.do(regularEmail)
while True:
    schedule.run_pending()
    time.sleep(1)