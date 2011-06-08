#!/usr/bin/python


class PostParserArgs:
    def __init__(self, required, type, db_name, default, parser):
        self.required = required
        self.type = type
        self.db_name = db_name
        self.default = default
        self.parser = parser

class PostParser:
    def __init__(self, all_params={}, allow_extra=True):
        self.allow_extra = allow_extra
        self.all_params = all_params
        self.extras = {}
        self.missing = []
        self.missing_req = []
        self.found = {}
        self.error = {}
        self.crit_error = False

    def add_params(self, all_params):
        self.all_params = all_params
        return
    
    def add_param(self, postvar, required=False, type="string", db_name="", default=None, parser=None):
        if postvar.strip() == "":
            return
        self.all_params.update({postvar: (required, type, db_name, default, parser)})
        return
    
    def get_extras(self):
        """Dictionary of all the parameters not in the parse"""
        return self.extras

    @staticmethod
    def convert_type(parg, convstr):
        if parg.parser == None:
            if parg.type == "string":
                return convstr
            else:
                return eval(parg.type + "(" + convstr + ")")
        else:
            return parg.parser(convstr)

    def save_as_attr(self, pvar, parg, val):
        if parg.db_name != "":
            setattr(self, parg.db_name, val)
        else:
            setattr(self, pvar, val)
    
    def parse(self, postvars):
        expecting_vars = self.all_params.keys()

        self.crit_error = False
        for pv in postvars.keys():
            
            # case #1, not expected
            if pv not in expecting_vars:
                self.extras.update({pv: postvars[pv]})
                setattr(self, pv, postvars[pv])
                continue
            
            # case #2, expected
            parg = self.all_params[pv]

            # convert to right type
            try:
                storeval = PostParser.convert_type(parg, postvars[pv])
            except Exception as e:
                self.error.update({pv: (postvars[pv], e)})
                self.crit_error = True
                storeval = parg.default

            # store as object attrib
            #self.found.update({pv: postvars[pv]})
            self.found.update({pv: storeval})
            self.save_as_attr(pv, parg, storeval)

        # figure out which ones are missing
        found_vars = self.found.keys()
        for v in expecting_vars:
            if v not in found_vars:

                parg = self.all_params[v]
                
                # case #1 we are required
                if parg.required:
                    self.missing_req.append(v)
                    self.crit_error = True
                # case #2 we are not required
                else:
                    self.missing.append(v)
                self.save_as_attr(v, parg, parg.default)
        
        return self.crit_error
                
    def get_log(self):
        retstr = "Found: {"
        for k, v in self.found.items():
            retstr += " " + k + ":" + str(v)
        retstr += " } Extras: {"
        for k, v in self.extras.items():
            retstr += " " + k + ":" + str(v)
        retstr += " } Missing: {"
        for k in self.missing:
            retstr += " " + k
        retstr += " } Missing-Required: {"
        for k in self.missing_req:
            retstr += " " + k
        retstr += " } Error: {"
        for k, v in self.error.items():
            retstr += " " + k + ":" + str(v)
        retstr += " }"
        return retstr



# from datetime import datetime


# upload_params = {
#     # (required, type, db_name, default, parser)
#     "device_id": PostParserArgs(True, "string", "device_id", "", None),
#     "aux_id": PostParserArgs(False, "string", "aux_id", "", None),
#     "misc": PostParserArgs(False, "string", "misc", "", None),
#     "record_datetime": PostParserArgs(True, "datetime", "record_datetime", datetime.now(), lambda x: datetime.fromtimestamp(float(x)/1000.0)),
#     "gps_latitude": PostParserArgs(False, "float", "gps_latitude", 0.0, None),
#     "gps_longitude": PostParserArgs(False, "float", "gps_longitude", 0.0, None),
#     "gps_altitude": PostParserArgs(False, "float", "gps_latitude", 0.0, None),
#     "mime_type": PostParserArgs(True, "string", "mime_type", "type/none", None),
#     "deployment_id": PostParserArgs(True, "string", "deployment_id", "Deployment", None),
#     "version": PostParserArgs(True, "string", "version", "0.0", None),
#     "tag": PostParserArgs(False, "string", "tag", "", None),
#     "data_type": PostParserArgs(False, "string", "data_type", "", None),
#     }
    

# upload_test = {"device_id": "t2ga4g", "record_datetime": "1285566129", "mime_type": "audio/wav", "deployment_id": "testD", "version": "0.0"}

# upload_test2 = {"device_id": "t2ga4g", "record_datetime": "1285566129", "mime_type": "audio/wav", "deployment_id": "testD", "version": "0.0", "Extrasauce": "5645"}

# upload_test3 = {"device_id": "t2ga4g", "record_datetime": "1285sdg29", "mime_type": "audio/wav", "deployment_id": "testD", "version": "0.0", "Extrasauce": "5645"}

# upload_test4 = {"device_id": "t2ga4g", "record_datetime": "128529", "deployment_id": "testD", "version": "0.0", "Extrasauce": "5645"}
