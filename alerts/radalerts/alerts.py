#!/usr/bin/env /proj/sot/ska3/flight/bin/python

"""
A package with MTA RadAlert class and related methods. Current application
is for radiation alerts. It could be used with dumps monitoring and
realtime alerts in the future.

Adding a new alert:
    - edit alert.json file
    - modify get_message() method if needed
    - create <new>alerts.py (e.g. radalerts.py, dumpalerts.py) and
      add a new method to radpars.py (or create dumpspar.py in the
      future) which will fetch the current value/data for verification

Disabling an alert:
    - touch <name>.log in the working directory to disable alerts for
      24 hours or extend the default 24h time period during which an
      alert is disabled after being triggered
    - or edit alerts.json and change manual_disable from 0 to 1.
"""

import os
import sys
import time
import numpy as np
import argparse
from pprint import pformat
from cxotime import CxoTime

#HOME = os.environ.get('HOME')
#PATH = f"{HOME}/git/radalerts"


class RadAlert(object):
    """
    RadAlert object
    """

    def __init__(self,
                 mode, # test, flight
                 name,
                 val,
                 lo,
                 hi,
                 type_, # bool, upper, lower, range
                 category, # caution, warning
                 url,
                 email,
                 action,
                 violation_type): # caution_lo, caution_hi, warning_lo, warning_hi, bool
        """
        """
        self.mode = mode
        self.name = name
        
        self.val = val
        self.lo = lo
        self.hi = hi
        self.type = type_
        self.category = category
        self.url = url
        self.email = email
        self.action = action
        self.logfile = f'{self.name}_{self.category}.log'
        self.violation_type = violation_type
        
        self.get_subject()
        self.get_message()


    def get_subject(self):
        """
        """
        if self.mode == 'test':
            self.subject = f'TEST {self.name}'
        else:
            self.subject = self.name


    def send_alert(self):
        """
        Send an alert email
        """
        cmd = f'cat {self.logfile} | mailx -s "{self.subject}" {self.email}'
        if self.mode == 'test':
            print(cmd)
        elif self.mode == 'flight':
            print(cmd)
            #os.system(cmd)
            
            
    def get_message(self):
        """
        RadAlert message
        """
            
        if self.type == 'bool':
            message = f"""{self.name} violation occured
"""
        else:
            message = f"""{self.name} violation occured ({self.violation_type})
Value: {self.val:.1e}
"""

        if self.type == 'upper':
            message = message + f"""Hi limit: {self.hi:.1e}
"""
        elif self.type == 'lower':
            message = message + f"""Lo limit: {self.lo:.1e}
"""
        elif self.type == 'range':
            message = message + f"""lo/hi: {self.lo:.1e}/{self.hi:.1e}
"""
        
        message = message + f"""{self.action}
This message sent to {self.email}
"""

        self.message = message


    def __repr__(self):
        return (' '.join([f'<{self.__class__.__name__}:',
                          f'mode={self.mode}',
                          f'email={self.email}',
                          f'name={self.name}',
                          f'logfile={self.logfile}',
                          f'val={self.val}>']))


    def __str__(self):
        return pformat(self.__dict__)
    
    
def get_current_hour():
    """
    Get current hour for the night time block
    of alerts (.e.g space weather)
    """
    t = time.ctime() # date and time
    t = t.split(' ')[-2] # time
    t = t.split(":")[0] # hour
    return int(t)


def remove_after_24h(fname):
    """
    Remove alert lock file after 24 hours
    Not all alerts will have a lock?
    dumps have one lock for a group of alerts?
    """
    t_created = os.stat(fname) # sec
    t_now = time.time() # sec
    dt = t_now - t_created.st_mtime
    if dt > 24 * 3600:
        os.remove(fname)


def trigger_alerts(a):
    """
    Check parameters against limits and trigger alerts
    with violations; record the type of violation and
    the violating values
    """

    name = a['name']
    val = a['val']
    
    trigger = {}
    
    if a['type'] == 'bool':
        trigger['bool'] = (not val)

    if a['type'] == 'upper':
        key = f"{a['category']}_hi"
        trigger[key] = val > a['hi']
                                   
    if a['type'] == 'lower':
        key = f"{a['category']}_lo"
        trigger[key] = val < a['lo']
        
    if a['type'] == 'range':

        hi = val > a['hi']
        lo = val < a['lo']
        
        if hi:
            key = f"{a['category']}_hi"
        elif lo:
            key = f"{a['category']}_lo"

        if hi or lo:
            trigger[key] = True
    
    # Both caution and warning violations will be recorded
    # for acep3_2h_fluence
    for k, v in trigger.items():
        
        if v:
            if a['triggered']:
                # alerts should not be enabled yet
                raise ValueError(f'RadAlert {name} should not be triggered before the check')

            a['violation_type'] = k
            a['triggered'] = True

    return a


def send_alert(a, mode, email):
    """
    """
    alert = RadAlert(mode=mode,
                  name=a['name'],
                  type_=a['type'],
                  category=a['category'],
                  val=a['val'],
                  lo=a['lo'],
                  hi = a['hi'],
                  url=a['url'],
                  email=email,
                  action=a['action'],
                  violation_type=a['violation_type'])

    if os.path.exists(alert.logfile):
        remove_after_24h(alert.logfile)
    else:
        with open(alert.logfile, "w") as fh:
            fh.write(alert.message)
        alert.send_alert()




