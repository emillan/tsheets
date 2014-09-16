Python wrapper for the TSheets REST API
===============================================================

An easy to use wrapper around the [Assembla API](http://api-doc.assembla.com/).

- [Installation](#installation)
- [Sample Usage](#sample-usage)


Installation
--------------------------------------------------

download and run setup.py install




Sample Usage
--------------------------------------------------
TSheets uses OAUTH2 for authentication and authorization.
This initial version of the wrapper does not provide methods for getting an access token but instead, uses the the already generated access token from a user's profile management page.


The following example connects to TSheets, retrieves the current user associated with the provide access token and lists that user's timesheets.

```python
from tsheets import api

tsclient = api.API("6b2ed705515648c2a436c271df37cb279e026868")

current_user = tsclient.get_current_user()
print current_user
timesheets = current_user.timesheets(start_date="2014-09-08", end_date="2014-09-14")
for timesheet in timesheets:
    print timesheet
# >>> <Doe, John>
# >>> <Timesheet #167528364: 2014-09-14 (2.72 hrs)>
# >>> <Timesheet #167077391: 2014-09-10 (4.22 hrs)>
# >>> <Timesheet #166757198: 2014-09-08 (4.60 hrs)>
# >>> <Timesheet #167077339: 2014-09-10 (1.08 hrs)>
# >>> <Timesheet #167357078: 2014-09-11 (1.71 hrs)>
# >>> <Timesheet #166935334: 2014-09-09 (3.00 hrs)>
# >>> <Timesheet #167206685: 2014-09-10 (5.48 hrs)>
# >>> <Timesheet #167218165: 2014-09-11 (2.81 hrs)>
# >>> <Timesheet #167070723: 2014-09-09 (3.19 hrs)>
# >>> <Timesheet #166920227: 2014-09-08 (5.08 hrs)>
# >>> <Timesheet #167390222: 2014-09-12 (6.22 hrs)>
# ...
```


