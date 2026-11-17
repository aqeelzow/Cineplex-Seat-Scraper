import os
import sys
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
pathToFile = os.path.join(script_dir, "form_data.json")
pathToAvailJson = os.path.join(script_dir, "available.json")

# ---- offer the last saved search ----
saved = None
if os.path.exists(pathToFile):
    with open(pathToFile) as f:
        saved = json.load(f)

if saved:
    email = list(saved.keys())[0]
    s = saved[email][0]
else:
    email = None
    s = None

if s:
    answer = input(f"Use last search ({s['movie']}, {', '.join(s['date'])})? [Y/n] ")
    if answer.strip().lower() != "n":
        from cineplex import runAll
        runAll(pathToFile, email, 0, pathToAvailJson, [], [])
        sys.exit()

def ask_list(question, separator=","):
    answer = input(question + " ").strip()
    return [x.strip() for x in answer.split(separator) if x.strip()]

# ---- questions ----
email = input("Your email: ").strip()
movie = input("Movie title (exactly as on Cineplex): ").strip()

theatres = ask_list("Theatre IDs, comma separated (check helper.py for IDs):")

# Dates contain a comma ("August 2, 2026"), so multiple dates are separated with ;
dates = ask_list("Dates, like August 2, 2026 (separate multiple dates with ;):", ";")
filters = ask_list("Filters, like IMAX (blank for none):")
exclude_rows = ask_list("Rows to skip, like A, B (blank for none):")
exclude_types = ask_list("Seat types to skip, like Wheelchair, Companion (blank for none):")

# ---- save in the format cineplex.py already reads ----
data = {email: [{
    "movie": movie,
    "theatreID": theatres,
    "date": dates,
    "filter": filters,
    "excludeSeat": exclude_rows,
    "excludeSeatType": exclude_types,
    "recipients": [email],
}]}

with open(pathToFile, "w") as f:
    json.dump(data, f, indent=2)

# Imported here so Chrome only starts after the questions are answered.
from cineplex import runAll

runAll(pathToFile, email, 0, pathToAvailJson, [], [])
