# Cineplex Seat Scraper

A Selenium-based scraper that checks Cineplex.com for available seats matching
a saved search (movie, theatre(s), date(s), and filters), and emails a
notification when matching seats are found.

## How it works

- `run.py` is the entry point. It loads a saved search from `form_data.json`
  and starts `runAll()`, which drives everything else.
- `cineplex.py` contains the scraper logic: it opens Cineplex.com in a
  headless Chrome window, selects the movie/date/theatre, applies filters,
  and inspects each showtime's seat map for available seats matching your
  criteria.
- On a schedule (every 5 seconds while running), it re-checks and writes the
  latest result to `available.json`.
- `emailSend.py` reads `available.json` and emails the result via Gmail SMTP.
- `helper.py` holds static reference data: theatre ID → name mapping, and
  seat type labels.

## Setup

1. Install dependencies:
   ```
   pip install selenium schedule python-dotenv
   ```
2. Make sure Chrome is installed. Selenium manages `chromedriver` itself
   (version 4.6+), so no separate driver download should be needed.
3. Create a `.env` file in this folder with your Gmail credentials:
   ```
   senderEmail=your_email@gmail.com
   GOOGLEPASS=your_gmail_app_password
   ```
   `GOOGLEPASS` must be a Gmail **App Password**, not your normal account
   password (Google requires this for SMTP login with 2FA enabled).
4. Fill out `form_data.json` (see schema below).
5. Run it:
   ```
   python run.py
   ```

## `form_data.json` schema
>MAKE SURE YOU ALSO CHANGE THE EMAIL ON LINE 15 OF `run.py` TO MATCH THE KEY ON `form_data.json`.

Keyed by the notification email address. Each key holds a list of saved
searches:

```json
{
  "your_email@gmail.com": [
    {
      "movie": "The Odyssey",
      "theatreID": ["7408", "7420"],
      "date": ["August 2, 2026"],
      "filter": ["IMAX 70mm"],
      "excludeSeat": ["A", "B", "AA"],
      "excludeSeatType": ["Wheelchair", "Companion"],
      "recipients": ["your_email@gmail.com"]
    }
  ]
}
```

| Field             | Type            | Notes |
|-------------------|-----------------|-------|
| `movie`           | string          | Must exactly match the title as listed on Cineplex.com. |
| `theatreID`       | list of strings | Theatre IDs as **strings** (see `helper.py`'s `theatresDict` for the full list). Must stay strings — several past bugs came from accidentally converting these to `int`. |
| `date`            | list of strings | Format: `"Month D, YYYY"` (e.g. `"August 2, 2026"`). Cineplex only lists near-term dates; a date outside its shown range is treated as "not found." |
| `filter`          | list of strings | Cineplex format filters (e.g. `"IMAX"`, `"VIP"`, `"Recliner"`, `"Sensory Friendly"`). See `helper.py`. |
| `excludeSeat`     | list of strings | Seat row letters to exclude (e.g. `"A"`, `"AA"`). |
| `excludeSeatType` | list of strings | Seat categories to exclude (e.g. `"Wheelchair"`, `"Companion"`). |
| `recipients`      | list of strings | Email addresses to notify. |

`run.py` selects which entry to run via `emailKey` and `emailEntry` (the
index into that email's list of saved searches) — both are hardcoded at the
top of `run.py` for this standalone version.

## Output — `available.json`

Written after every scrape cycle, in the shape:
```json
["<status message>", "<details or list of seat matches>", "<HH:MM:SS timestamp>"]
```
`emailSend.py` reads this file to compose the notification email.

## Running headless

Chrome runs headless by default (`--headless=new` in `cineplex.py`'s Chrome
options) so no browser window pops up. If you need to visually debug a
selector or page-state issue, comment out the `--headless=new` line
temporarily so you can watch what the scraper is actually doing.

## Known quirks / gotchas

- **Theatre IDs must stay strings end-to-end.** `theatresDict` in `helper.py`
  is keyed by string IDs (`"7408"`, not `7408`). Converting a theatre ID to
  `int` anywhere before it's used to look up a theatre name will raise
  `KeyError`.
- **Movie titles must match exactly**, including punctuation, or the scraper
  reports "movie not found" and stops that cycle.
- **Dates must be within Cineplex's currently listed showtime window.** A
  date too far in the future (not yet posted) is indistinguishable from a
  typo — both show up as "date not found."
- The scraper catches `TimeoutException` and `MaxRetryError` around the main
  loop, but Selenium/network failures can raise other exception types
  (`SessionNotCreatedException`, `ReadTimeoutError`,
  `StaleElementReferenceException`, etc.). If the process exits unexpectedly,
  check the traceback for the exception type and consider adding it to the
  catch list, or wrap the scheduler loop in a broad `except Exception` if
  reliability matters more than surfacing every failure type immediately.
- If Chrome fails to launch at all (`SessionNotCreatedException: Chrome
  instance exited`), it's usually a stale `chromedriver` cache after a Chrome
  auto-update, or leftover zombie `chrome.exe`/`chromedriver.exe` processes
  from a previous crashed run — kill those and/or run
  `pip install -U selenium` to refresh Selenium Manager's driver cache.

## Project structure

```
.
├── run.py          # entry point — loads form_data.json, starts the scraper
├── cineplex.py      # scraper logic + scheduling loop
├── emailSend.py      # reads available.json, sends the notification email
├── helper.py          # theatre ID map, seat type labels
├── form_data.json      # your saved search(es) — see schema above
├── available.json        # latest scrape result (auto-generated)
└── .env                    # GOOGLEPASS=... (not committed)
```
