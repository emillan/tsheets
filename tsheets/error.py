import json
from exceptions import Exception



class TSheetsError(Exception):
    """
    TSheets Error Handler
    """

    def __init__(self, status_code, response, *args, **kwargs):
        self.error_dict = json.loads(response)
        self.status_code = str(status_code)
        if self.error_dict.has_key('error_description'):
            self.error_code = self.error_dict['error']
            self.error_message = self.error_dict['error_description']
        else:
            self.error_code = self.error_dict['error']['code']
            self.error_message = self.error_dict['error']['message']

    def __str__(self):
        return "{}: {}".format(self.error_code, self.error_message)

    def __repr__(self):
        return self.__str__()
