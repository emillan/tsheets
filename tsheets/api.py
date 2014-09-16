import requests
from httplib import HTTPException
from .models import (User,
                     CurrentUser,
                     Timesheet,
                     Jobcode,
                     JobcodeAssignment,
                     PayrollReport)
from .error import TSheetsError


class API(object):
    """
    The API client class which provides access to the TSheets REST API endpoints
    """

    _base_url = "https://rest.tsheets.com/api/v1/"
    _auth_header = None
    _session = None
    __auth_token = None
    __auth_key = None
    __auth_secret = None

    def __init__(self, auth_token):
        """
        TODO: modify initializer to accept KEY and SECRET as parameters
        """
        self.__auth_token = auth_token
        url = self._base_url + "users"
        self._auth_header = {'Authorization': "Bearer {}".format(auth_token)}
        self._session = requests.Session()
        self._session.headers.update(self._auth_header)
        response = self._session.get(url)

        if response.status_code != 200:
            raise TSheetsError(response.status_code, response.content)
        else:
            return None

    def __get_TSObjects(self, model, **kwargs):
        """
        the private method which fetches data from TSheets
        
        args:
            model (class) : the TSheetsObject class which provides API endpoint information
            kwargs: all keyword arguments appropriate for the endpoint
            
        returns:
            JSON response (dict) : when `return_json` in kwargs is True, method will return the raw dict response
                                      from the API
            List of TSheetsObject (model) : when `return_json` is not present in kwargs, method will return a list of
                                      objects of <model> type
        
        raises:
            TSheetsError
            HTTPException
        """
        # TODO: modify this method so it can handle POST requests (for API's insert/create operations)
        #       or create a separated method.  haven't decided yet. :p

        url = self._base_url + model._endpoint_name
        payload = {}
        result = []

        payload.update(**kwargs)

        return_json = payload.get('return_json', False)
        payload.pop('return_json', None)

        try:
            response = self._session.get(url, params=payload)
            if response.status_code == 200:
                if return_json: return response.json()
                tsobject_results = response.json()['results'][model._result_object_key]
                # TODO: add code to handle supplemental data and more
                tsobjects = tsobject_results.values() if hasattr(tsobject_results, 'values') else tsobject_results
                for tsobject in tsobjects:
                    model_instance = model(api=self, **tsobject)
                    result.append(model_instance)
                return result
            else:
                raise TSheetsError(response.status_code, response.content)
        except HTTPException as error:
            raise error

    def get_json(self, model, **kwargs):
        """
        returns the raw json object from the API endpoint for `model`
        """
        return self.__get_TSObjects(model, return_json=True, **kwargs)

    def get_current_user(self):
        """
        returns a User object associated with the current access token.
        """
        user_list = self.__get_TSObjects(CurrentUser)
        return user_list[0]

    def list_users(self, **kwargs):
        """
        Retrieves a list of all users associated with the current user's company.
        
        Optional arguments used to filter results: 
            ids (str)       : Comma separated list of one or more user ids you'd like to filter on.
            usernames (str) : Comma separated list of one or more usernames you'd like to filter on.
            active (str)    : 'yes', 'no', or 'both'. Default is 'yes'.
            first_name (str): * will be interpreted as a wild card.
                                 Starts matching from the beginning of the string.
            last_name (str) :  * will be interpreted as a wild card.
                                 Starts matching from the beginning of the string.
            modified_before (str) : (ISO8601 format). Only users modified before this date/time will be returned 
                                       (i.e. 2004-02-12T15:19:21+00:00).
            modified_since (str)  : (ISO8601 format). Only users modified since this date/time will be returned
                                       (i.e. 2004-02-12T15:19:21+00:00).
            per_page (int)        : Represents how many results you'd like to retrieve per request (page).
                                       Default is 50. Max is 50.
            page (int)            : Represents the page of results you'd like to retrieve.
        
        see: http://developers.tsheets.com/docs/api/users/list-users
        """
        return self.__get_TSObjects(User, **kwargs)

    def list_jobcodes(self, **kwargs):
        """
        Retrieves a list of all jobcodes associated with your company, with optional filters to narrow down the results.
        
        optional keyword arguments:
            ids (str)        : Comma separated list of one or more jobcode ids you'd like to filter on. Only jobcodes
                                  with an id set to one of these values will be returned. If omitted, all jobcodes
                                  matching other specified filters are returned.
            parent_ids (str) : Default is -1 (meaning all jobcodes will be returned regardless of parent_id). 
                                  Comma separated list of one or more jobcode parent_ids you'd like to filter on.
                                  Only jobcodes with a parent_id set to one of these values will be returned.
                                  Additionally you can use 0 to get only the top-level jobcodes. Then get the id
                                  of any results with has_children=yes and feed that in as the value of parent_ids
                                  for your next request to get the 2nd level of jobcodes, and so on, to traverse
                                  an entire tree of jobcodes. 

                                  Use `-1` to return all jobcodes regardless of parent_id; this is especially useful
                                  when combined with the modified_since filter. When parent_ids is -1, you'll have
                                  the jobcode records needed to trace each result back to it's top level parent in
                                  the supplemental_data section of the response.
            type (str)     : regular, pto, or all. Default is regular.
            active (str)   : 'yes', 'no', or 'both'. Default is 'yes'. If a jobcode is active, it is available
                                 for selection during time entry.
            per_page (int) : Represents how many results you'd like to retrieve per request (page).
                                Default is 50. Max is 50.
            page (int)     : Represents the page of results you'd like to retrieve.

            modified_before (str) : (ISO8601 format). Only jobcodes modified before this date/time will be returned
                                       (i.e. 2004-02-12T15:19:21+00:00).
            modified_since (str)  : (ISO8601 format). Only jobcodes modified since this date/time will be returned
                                       (i.e. 2004-02-12T15:19:21+00:00).
                                       
        see: http://developers.tsheets.com/docs/api/jobcodes/list-jobcodes
        """
        return self.__get_TSObjects(Jobcode, **kwargs)

    def list_jobcode_assignments(self, **kwargs):
        """
        Retrieves a list of all jobcode assignments associated with users
        
        Optional keyword arguments:
            user_ids (str)    : Comma separated string of one or more user ids for whom you'd like to retrieve
                                   jobcode assignments. If none are specified, all jobcode assignments (which you have
                                   rights to view) will be returned. Only jobcode assignments belonging to these
                                   user_ids or where the jobcode assigned_to_all property is true will be returned.
                                   
                                   Results where assigned_to_all is true for a jobcode are indicated by a user_id value
                                   of 0 for the jobcode_assignment object. To view jobcode assignments for users other
                                   than yourself you must be an admin or a group manager or have the manage_users
                                   permission or the manage_jobcodes permission.
            type (str)        : Refers to the jobcode type - regular, pto, or all. Defaults to regular.
            
            jobcode_parent_id (int) : When omitted, all jobcode assignments are returned regardless of jobcode parent.
                                         If specified, only assignments for jobcodes with the given jobcode parent_id
                                         are returned. To get a list of only top-level jobcode assignments,
                                         pass in a jobcode_parent_id of 0.
            active (str)      : yes, no, or both. Default is both. Yes means the assignment is active,
                                   no means it is deleted/inactive.
            modified_before (str) : (ISO8601 format). Only jobcode assignments modified before this date/time will be
                                       returned (i.e. 2004-02-12T15:19:21+00:00).
            modified_since (str)  : (ISO8601 format). Only jobcode assignments modified since this date/time will be
                                        returned (i.e. 2004-02-12T15:19:21+00:00).
            per_page (int)        : Represents how many results you'd like to retrieve per request (page).
                                       Default is 50. Max is 50.
            page (int)            : Represents the page of results you'd like to retrieve.
        
        see: http://developers.tsheets.com/docs/api/jobcode_assignments/list-jobcode-assignments
        """
        return self.__get_TSObjects(JobcodeAssignment, **kwargs)

    def list_timesheets(self, **kwargs):
        """
        Retrieves a list of all timesheets associated with your company
        
        Keyword arguments:
            ids (str)        : required - unless modified_before, modified_since, or start_date and end_date are set
                                  Comma separated list of one or more timesheet ids you'd like to filter on.
                                  Only timesheets with an id set to one of these values will be returned. If omitted,
                                  all timesheets matching other specified filters are returned.
            start_date (str) : required - unless modified_before, modified_since, or ids is set
                                  YYYY-MM-DD formatted date. Any timesheets with a date falling on or after this date
                                  will be returned.
            end_date (str)   : required - unless modified_before, modified_since, or ids is set)
                                  YYYY-MM-DD formatted date. Any timesheets with a date falling on or before this date
                                  will be returned.
            jobcode_ids (str): optional. comma-separated string of jobcode ids. Only time recorded against these
                                  jobcodes or one of their children will be returned.
            user_ids (str)   : optional. comma-separated list of user ids. Only timesheets linked to these users will
                                  be returned.
            group_ids (str)  : optional. a comma-separated list of group ids. Only timesheets linked to users from
                                  thesegroups will be returned.

            on_the_clock (str) : optional. 'yes', 'no', or 'both'. Default is 'no'. If a timesheet is on_the_clock,
                                    it means the user is currently working (has not clocked out yet).
            jobcode_type (str) : optional. 'regular', 'pto', or 'both'. Default is 'both'. Only timesheets linked
                                    to a jobcode of the given type are returned.

            modified_before (str) : required - unless modified_since, ids, or start_date and end_date are set
                                       (ISO8601 format). Only timesheets modified before this date/time will be
                                       returned (i.e. 2004-02-12T15:19:21+00:00).
            modified_since (str)  : required - unless modified_before, ids, or start_date and end_date are set
                                        (ISO8601 format). Only timesheets modified since this date/time will be
                                        returned (i.e. 2004-02-12T15:19:21+00:00).
            per_page (int)  : optional. Represents how many results you'd like to retrieve per request (page).
                                 Default is 50. Max is 50.
            page (int)      : optional. Represents the page of results you'd like to retrieve. Default is 1.
            
        see: http://developers.tsheets.com/docs/api/timesheets/list-timesheets
        """
        return self.__get_TSObjects(Timesheet, **kwargs)

    def get_payroll_report(self, **kwargs):
        """
        Retrieves a payroll report associated with a timeframe
        
        Keyword arguments:
            start_date (str)    : required. YYYY-MM-DD formatted date. Any time with a date falling on or after
                                     this date will be included.
            end_date (str)      : required. YYYY-MM-DD formatted date. Any time with a date falling on or before
                                     this date will be included.
            user_ids (str)      : optional. comma-separated list of user ids. Only time for these users will be included
            group_ids (str)     : optional. comma-seperated list of group ids. Only time for users from these groups
                                     will be included.
            include_zero_time (str) : optional. 'yes' or 'no'. Default is 'no'. If 'yes', all users will be included
                                         in the output, even if they had zero hours for the time period.
                                         
        see: http://developers.tsheets.com/docs/api/reports/payroll-report
        """
        return self.__get_TSObjects(PayrollReport, **kwargs)

    def list_jobcodes_by_user(self, user_ids, exclude_global=True, **kwargs):
        """
        Returns a list of all user_jobcodes assigned to users whose ids are in `user_ids`
        (excluding parent user_jobcodes). By default, returns all active user_jobcodes.
        
        args:
            exclude_global (bool) : If True, this method will exclude Jobode that are assigned to All users
            kwargs: see `API.list_jobcode_assignments` method

        raises:
           TsheetsError
           HTTPException
           
        return data format:
        {
        "<user_id>": {
            "user": <user object>,
            "user_jobcodes": [
                <jobcode object>,
                <jobcode object>,
                <jobcode object>,
                ]
            }
        }
        """
        excl = exclude_global or kwargs.get('exclude_global', False)
        kwargs.pop('exclude_global', None)
        tmp_active = kwargs.get('active', 'yes')
        kwargs.update({'active': tmp_active})

        kwargs.update({'user_ids': str(user_ids)})

        raw_assignments = self.get_json(JobcodeAssignment, **kwargs)
        if not raw_assignments.get('supplemental_data'):
            return None

        users = raw_assignments.get('supplemental_data').get("users", {})
        # initialize result with user_ids as keys, and user objects in values
        result = {u["id"]:{"user": User(api=self, **u), "jobcodes": []} for u in users.values()}
        assignments = raw_assignments.get("results").get("jobcode_assignments", {})
        jobcodes = raw_assignments.get('supplemental_data').get('jobcodes', {})

        for uid, udata in result.iteritems():
            user_jobcode_ids = [a["jobcode_id"] for a in assignments.values() if a["user_id"] == uid]
            user_jobcodes = [Jobcode(api=self, **j) for j in jobcodes.values() \
                                if j["id"] in user_jobcode_ids and not j['has_children']]
            if excl:
                user_jobcodes = [j for j in user_jobcodes if j.assigned_to_all]
            udata["jobcodes"] = user_jobcodes
            result[uid] = udata
        return result

    def grouped_timesheets(self, user_ids, start_date, end_date, active='yes', exclude_global=False):
        """
        returns timesheets grouped by jobcodes indexed by user id following this structure:
        {
           "<user_id 1>": {
               "user": <user_object>,
               "jobcodes": {
                   "<jobcode_id>": { 
                       "total_hours": 0.0,
                       "timesheets": [ 
                           <timesheet object>,
                           <timesheet object>,
                        ],
                        "jobcode": <jobcode object>
                   },
                },
               "summary": {"total_hours": 0.0}                              
           },
           "<user_id 2>": {
               "user": <user_object>,
               "jobcodes": {
                   "<jobcode_id>": { 
                       "total_hours": 0.0,
                       "timesheets": [ 
                           <timesheet object>,
                           <timesheet object>,
                        ],
                        "jobcode": <jobcode object>
                   },
                },
               "summary": {"total_hours": 0.0}                              
           },
        }
        """
        # ensure that there are no spaces before of after commas
        user_ids = str(user_ids)
        uids = [uid.strip() for uid in user_ids.split(",")]
        user_ids = ",".join(uids)

        jobcodes = self.list_jobcodes_by_user(user_ids=user_ids, active=active, exclude_global=exclude_global)
        ts_json = self.get_json(Timesheet, user_ids=user_ids, start_date=start_date, end_date=end_date)
        timesheets = ts_json["results"]["timesheets"].values()
        users = ts_json["supplemental_data"]["users"]

        grouped_ts = {int(uid):{"user":None, "jobcodes":{}, "summary":{}} for uid in uids}
        all_user_hours = 0.0

        for user_id, user_data in grouped_ts.iteritems():
            user_data["user"] = User(api=self, **users[str(user_id)])
            user_total_hours = 0.0
            user_jobcodes = jobcodes[user_id]["jobcodes"]
            tmp_jobcodes = {}
            for jobcode in user_jobcodes:
                tmp_jobcodes[str(jobcode.id)] = {}
                # create a list of Timesheet objects
                user_ts = [Timesheet(api=self, **ts) for ts in timesheets if ts["jobcode_id"] == jobcode.id]
                ts_hours = sum([uts.tshours for uts in user_ts])
                user_total_hours += ts_hours
                # total hours per jobcode
                tmp_jobcodes[str(jobcode.id)]["total_hours"] = ts_hours
                tmp_jobcodes[str(jobcode.id)]["jobcode"] = jobcode
                tmp_jobcodes[str(jobcode.id)]["timesheets"] = user_ts
            all_user_hours += user_total_hours
            user_data["jobcodes"] = tmp_jobcodes
            # total hours per user
            user_data["summary"]["total_hours"] = user_total_hours
            grouped_ts[user_id] = user_data
        grouped_ts.update({"summary":{"total_hours": all_user_hours}})

        return grouped_ts
