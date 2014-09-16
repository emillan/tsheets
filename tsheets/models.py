import datetime


class BaseTSheetObject(object):
    id = None
    _endpoint_name = None
    _result_object_key = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class User(BaseTSheetObject):
    """
    TSheets User
    
    an instance of this class will have the following attributes:
        id (int)           : Read-only. Id of this user.
        username (str)     : Username associated with this user.
        email (str)        : Email address associated with this user.
        first_name (str)   : First name of user.
        last_name (str)    : Last name of user.
        group_id (int)     : Id of the group this user belongs to.
        salaried (bool)    : 
        exempt (bool)      :
        payroll_id (str)   : Read-only. Unique string associated with this user. 
                                Usually used for linking with external systems.
        client_url (str)   : Read-only. Client account url identifier associated with this user.
        
        employee_number (int) : Unique number associated with this user. For your reference only.
        
        mobile_number (str): Mobile phone number associated with this user.
        hire_date (str)    : YYYY-MM-DD formatted date upon which this user was hired.
        term_date (str)    : YYYY-MM-DD formatted date upon which this user's employment was terminated.
        last_active (str)  : (ISO8601 format). Read-only. Date/time when this user last performed any action
                                within TSheets (i.e. 2004-02-12T15:19:21+00:00).
        active (bool)      : If False, this user is considered archived.
        approved_to (str)  : YYYY-MM-DD formatted date indicating the latest date 
                                this user has had timesheets approved to (if approvals addon is installed).
        submitted_to (str) : YYYY-MM-DD formatted date indicating the latest date this user has 
                                submitted timesheets up to (if approvals addon is installed).
        last_modified (str) :(ISO8601 format). Read-only. Date/time when this user was last modified
                                (i.e. 2004-02-12T15:19:21+00:00).
        created (str)       : String (ISO8601 format). Read-only. Date/time when this user was created
                                (i.e. 2004-02-12T15:19:21+00:00).
        permissions (dict)  : Permissions with a True/False value for each that apply to this user.
        
                                admin                : Administrator, can perform any changes on the account.
                                mobile               : Able to use mobile devices to record time.
                                see_who_is_working   : Able to view the list of who's currently working for the company.
                                reports              : Able to run/view all reports for the company.
                                manage_timesheets    : Able to create/edit/delete timesheets for anyone in the company.
                                manage_authorization : Able to manage computer authorization for the company.
                                manage_users         : Able to create/edit/delete users, groups, and managers
                                                          for the entire company.
                                manage_my_timesheets : Ability to completely manage their own timesheets.
                                manage_fields        : Able to create/edit/delete jobcodes and custom field items
                                                          for the entire company.
                                approve_timesheets   : Able to run approval reports and approve time for all employees.
    
    see: http://developers.tsheets.com/docs/api/users/user-object
    """

    _endpoint_name = "users"
    _result_object_key = "users"

    def jobcode_assignments(self, exclude_global=True, **kwargs):
        """
        returns all jobcode_assignment for this user.
        
        args:
           exclude_global (boolean): if set to True, results will exclude jobcode_assignments
              that are assigned to all users (denoted by `assigned_to_all`='true')
           kwargs : keyword arguments (see `list_jobcode_assignments` method)
        
        raises:
           TsheetsError
           HTTPException
        """
        if not self.api: return []
        kwargs.update({"user_ids":self.id})
        excl = exclude_global or kwargs.get('exclude_global', False)
        kwargs.pop('exclude_global', None)

        assignments = self.api.list_jobcode_assignments(**kwargs)
        if excl:
            assignments = [a for a in assignments if a.user_id == self.id]
        return assignments

    def timesheets(self, **kwargs):
        """
        returns a list of timesheets for this user.
        
        args:
            see: `API.list_timesheets` method

        raises:
           TsheetsError
           HTTPException
        """
        if not hasattr(self, 'api'): return []

        kwargs.update({"user_ids":self.id})
        return self.api.list_timesheets(**kwargs)

    def jobcodes(self, exclude_global=True, **kwargs):
        """
        returns a list of all jobcodes assigned to this user (excluding parent jobcodes or folders).
        by default, returns all active jobcodes.
        
        args:
            exclude_global (bool) : If True, this method will exclude Jobode that are assigned to All users
            kwargs: see `API.list_jobcode_assignments` method

        raises:
           TsheetsError
           HTTPException
        """

        result = []
        excl = exclude_global or kwargs.get('exclude_global', False)
        kwargs.pop('exclude_global', None)
        tmp_active = kwargs.get('active', 'yes')
        kwargs.update({'active': tmp_active})
        kwargs.update({'user_ids': str(self.id)})
        assignments = self.api.get_json(JobcodeAssignment, **kwargs)

        if assignments.get('supplemental_data'):
            jcodes = assignments.get('supplemental_data').get('jobcodes')
            if jcodes:
                result = [Jobcode(api=self.api, **j) for j in jcodes.values() if not j['has_children']]
                if excl:
                    result = [j for j in result if j.assigned_to_all ]
        return result

    def grouped_timesheets(self, start_date, end_date, active='yes', exclude_global=False):
        """
        returns this user's Timesheets grouped by jobcodes in the following structure:
        {
            "jobcodes": {
                "<jobcode_id>": { 
                   "total_hours": 0.0,
                   "timesheets": [ 
                        <timesheet object>,
                        <timesheet object>, 
                        ...
                        ],
                    "jobcode": <jobcode object>
                },
            },
            "summary": {"total_hours": 0.0}                              
        }
        """
        ts = self.api.grouped_timesheets(self.id, start_date, end_date,
                                         active=active, exclude_global=exclude_global)
        gts = ts.get(self.id, {})
        gts.pop("user", None)
        return gts

    def __repr__(self):
        return "<{}, {}>".format(self.last_name, self.first_name)


class CurrentUser(User):
    """
    A subclass of User which is used to represent the user associated with the current access token
    """
    _endpoint_name = "current_user"
    _result_object_key = "users"


class Jobcode(BaseTSheetObject):
    """
    Jobcode object

    Attributes:
        id (int)         : Id of jobcode.
        parent_id (int)  : Id of this jobcode's parent. 0 if it's top-level.
        name (str)       : Name of the jobcode. Must be unique for all jobcodes that share the same parent_id.
        short_code (str) : This is a shortened code or alias that is associated with the jobcode.
                              It may only consist of letters and numbers. Must be unique for all jobcodes that share
                              the same parent_id. If the Dial-in Add-on is installed, this field may only consist
                              of numbers since it is used for jobcode selection from touch-tone phones.
        type (str)       : Read-only. 'regular' or 'pto'. Indicates jobcode type. Additional types may be added 
                              in the future.
        active (bool)    : If True, this jobcode is active. 
                              If False, this jobcode is archived. To archive a jobcode, set this field to false.
                              When a jobcode is archived, any children underneath the jobcode are archived as well.
                              Note that when you archive a jobcode, any jobcode assignments or customfield
                              dependencies are removed.

                              To restore a jobcode, set this field to true. When a jobcode is restored, any parents
                                 of that jobcode are also restored.
        billable (bool)  : Indicates whether this jobcode is billable or not.
        
        billable_rate (float) : Dollar amount associated with this jobcode for billing purposes.
                                   Only effective if billable is true.
        has_children (bool)   : Read-only. If True, there are jobcodes that exist underneath this one, so this jobcode
                                   should be treated as a container or folder with children jobcodes underneath it.
        assigned_to_all (bool): Indicates whether this jobcode is assigned to all employees or not.
        last_modified (str)   : (ISO8601 format). Read-only. Date/time when this jobcode was last modified
                                   (i.e. 2004-02-12T15:19:21+00:00).
        created (str) :       : String (ISO8601 format). Read-only. Date/time when this jobcode was created
                                   (i.e. 2004-02-12T15:19:21+00:00).
                                   
        filtered_customfielditems (dict) : Displays which customfielditems should be displayed when this jobcode
                                              is chosen for a timesheet. Each property of the object is a customfield
                                              with its value being an array of customfielditem id         
        required_customfields (list of int): Ids of customfields that should be displayed when this jobcode
                                                is selected on a timecard.
        
    see: http://developers.tsheets.com/docs/api/jobcodes/jobcode-object
    """

    _endpoint_name = "jobcodes"
    _result_object_key = "jobcodes"

    def __repr__(self):
        return "<Job Code #{}: {}>".format(self.id, self.name)


class JobcodeAssignment(BaseTSheetObject):
    """
    A jobcode assignment represents that a user has access to a given jobcode for selection while tracking time.
    A jobcode is considered 'assigned' if the jobcode has been specifically assigned to a person, or if the jobcode has
    the assigned_to_all property set to True.
    
    Attributes:
        id (int)        : Read-only. Id of jobcode assignment.
        user_id (int)   : Id of the user that this assignment pertains to.
        jobcode_id (int): Id of the jobcode that this assignment pertains to.
        active (bool)   : Whether or not this assignment is 'active'. If false, then the assignment has been deleted.
                             true means it is in force.  
        created (str)   : (ISO8601 format). Read-only. Date/time when this jobcode assignment was created
                             (i.e. 2004-02-12T15:19:21+00:00).                             
        last_modified (str) : (ISO8601 format). Read-only. Date/time when this jobcode assignment was last modified
                             (i.e. 2004-02-12T15:19:21+00:00).
    
    see: http://developers.tsheets.com/docs/api/jobcode_assignments/jobcode-assignment-object
    """

    _endpoint_name = "jobcode_assignments"
    _result_object_key = "jobcode_assignments"

    def __repr__(self):
        return "<Job Code Assignment #{}>".format(self.id)


class Timesheet(BaseTSheetObject):
    """
    A user's timesheet
    
    Attributes:
        id (int)           : Read-only. Id of timesheet.
        user_id (int)      : User id for the user that this timesheet belongs to.
        jobcode_id (int)   : Jobcode id for the jobcode that this timesheet is recorded against.
        locked (int)       : If greater than 0, the timesheet is locked for editing. A timesheet could be locked
                                for various reasons, such as being approved, invoiced, etc.
        notes (str)        : Notes associated with the timesheet.
        customfields (str) : Only present if the Custom Fields Add-On is installed. This will be a key => value
                                array of customfield ids and customfield items that are associated with the timesheet.
        created (str)      : (ISO8601 format). Read-only. Date/time when this object was created
                                (i.e. 2004-02-12T15:19:21+00:00).
        last_modified (str): (ISO8601 format). Read-only. Date/time when this object was last modified
                                (i.e. 2004-02-12T15:19:21+00:00).
        type (str)         : Either 'regular' or 'manual'. Regular timesheets have a start/end time
                                (duration is calculated by TSheets). Manual timesheets have a date and a duration
                                (in seconds). Unique properties for each timesheet type are below.
        on_the_clock (bool): Read-only. If True, the user is currently on the clock (i.e. not clocked out,
                                so end time is empty). If False, the user is not currently working on this timesheet.
                                Manual timesheets will always have this property set as false.

        **Regular Timesheets**
            start (str)    : (ISO8601 format). Date/time that represents the start time of this timesheet
                                (i.e. 2004-02-12T15:19:21+00:00).
            end (str)      : (ISO8601 format). Date/time that represents the end time of this timesheet
                                (i.e. 2004-02-12T15:19:21+00:00). Enter an empty string to make the timesheet active.
            date (str)     : Read-only. YYYY-MM-DD formatted date. The timesheet's date.
            duration (int) : Read-only. The total number of seconds recorded for this timesheet.

        **Manual Timesheets**
            start (str)    : Not applicable. Will always be an empty string.
            end (str)      : Not applicable. Will always be an empty string.
            date (str)     : YYYY-MM-DD formatted date. The timesheet's date.
            duration (int) : The total number of seconds recorded for this timesheet.
    
    see : http://developers.tsheets.com/docs/api/jobcode_assignments/jobcode-assignment-object
    """

    _endpoint_name = "timesheets"
    _result_object_key = "timesheets"

    @property
    def tshours(self):
        """
        returns this timesheet's duration in hours
        """
        try:
            return self.duration / 3600.0
        except:
            return 0.0

    @property
    def tsdate(self):
        """
        returns this timesheet's date as Date object
        """
        if not self.date:
            return None
        return datetime.datetime.strptime(self.date, '%Y-%m-%d').date()

    def __repr__(self):
        return "<Timesheet #%s: %s (%.2f hrs) >" % (self.id, self.date, self.tshours)


class PayrollReport(BaseTSheetObject):
    """
    Payroll report associated with a timeframe
    
    
    Attributes:
        user_id (int)           : id of the user associated with the payroll report
        client_id (str)         : id of the client
        start_date (str)        : YYYY-MM-DD start_date of the payroll reporting timeframe
        end_date (str)          : YYYY-MM-DD end_date of the payroll reporting timeframe
        total_re_seconds (int)  : regular time, in seconds
        total_ot_seconds (int)  : overtime time, in seconds
        total_dt_seconds (int)  : doubletime time, in seconds
        total_pto_seconds (int) : total 'Paid Time-off' time, in seconds
        total_work_seconds (int): total overall time, in seconds 
        pto_seconds (dict)      : break-down of PTO time by PTO code indexed by PTO code id
        
    see: http://developers.tsheets.com/docs/api/reports/payroll-report
    """

    _endpoint_name = "reports/payroll"
    _result_object_key = "payroll_report"

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Payroll Report for user #{} {}-{}>".format(self.user_id, self.start_date, self.end_date)
