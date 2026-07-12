from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
import json
import os

### checkshowtime() - add exception if throws cant find aria label
### checkshowtime() - add hard check to see if seats have rendered rather than sleeping 1
### can't filter out 4DX & VIP Seats
### rather than quit after one wrong date/theatre, make it so that it skips.
### if none of the filters exist, click x instead of quitting

# theatre name: id
theatres = {
    7408: "Cineplex Cinemas Vaughan",
    7420: "Cineplex Cinemas Mississauga Square One"
}

seatTypes = ["Wheelchair", "Standard", "Companion", "D-BOX*" ]



# Initialize the driver
driver = webdriver.Chrome()
script_dir = os.path.dirname(os.path.abspath(__file__))
wait = WebDriverWait(driver, 20)
with open(os.path.join(script_dir, "form_data.json"), "r") as openFile:
    data = json.load(openFile)

excludeType = ["Wheelchair", "Companion"]
excludeSeat = ["A", "B", "C"]
movieTitle = "The Odyssey"

movieTheatres = data["theatre_id"]
filterList = data["filters"]
movieDates = data["dates"]
showtimeIDs = []
availableShowtimes = []

## Claude code
def safeClick(element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    try:
        element.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", element)

def writeToAvail():
    with open(os.path.join(script_dir, "available.json"), "w") as writeFile:
        json.dump(availableJSON, writeFile)


def quit(subject, bodyText):
    global availableJSON
    availableJSON = [subject, bodyText]
    driver.quit()
    writeToAvail()
def start():
    driver.get("https://www.cineplex.com/?openTM=true")
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#onetrust-accept-btn-handler")))
    safeClick(driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-handler"))
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
            print("\nsuccess")
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
            print("\nsuccess")
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
            print("\nsuccess")
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
                print("\nsuccess")
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
def checkShowtime(theatreID, showtimeID):
    #global availableJSON
    main_tab = driver.current_window_handle
    driver.switch_to.new_window('tab')
    url = f"https://www.cineplex.com/ticketing/preview?theatreId={theatreID}&showtimeId={showtimeID}&dbox=false"
    driver.get(url)

    # Locate a single element
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='seat-'] > g.SeatElement_seatLinkButton__wxQzX")))
    time.sleep(1)
    childElements = driver.find_elements(By.CSS_SELECTOR, "[class*='seat-'] > g.SeatElement_seatLinkButton__wxQzX")
    for element in childElements:
        exclude = False
        try:
            status = element.get_attribute("aria-label").casefold()
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
                    availableShowtimes.append(url + ":" + element.get_attribute("aria-label"))
            '''else:
                availableJSON = ["No seats were found.", "That's odd, we couldn't find any seats."]
                driver.quit()
                writeToAvail()'''

                #print(element.get_attribute("aria-label"))
        except StaleElementReferenceException:
            continue
    driver.close()
    driver.switch_to.window(main_tab)

"""
movieDates = ["July 16, 2026", "July 17, 2026", "July 18, 2026"]
movieTheatres = [7408, 7420]
filterList = ["IMAX 70mm"]
"""




if driver.session_id is not None:
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
            availableJSON = ["No showtime exists for "+movieTitle, "Hang on tight! Hopefully more showtimes will arrive for " +movieTitle+"."]
            driver.quit()
            writeToAvail()
        else:
            for showtime in showtimeIDs:
                    print(f"\n\n{theatres[theatre]}")
                    checkShowtime(theatre, showtime)
    if len(availableShowtimes) == 0:
        availableJSON = ["No available seats for "+movieTitle, "Hang on tight! Hopefully more seats will arrive for " +movieTitle+"."]
    else:
        availableJSON = ["There are " + str(len(availableShowtimes))+ " available seats for " + movieTitle, availableShowtimes]
    writeToAvail()
