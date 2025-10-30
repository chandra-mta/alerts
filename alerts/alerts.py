"""
A package with MTA Alert class and related methods.
Current application covers the usecase of satellite alerts and radiation alerts,
with possible future implementations of dumps monitoring.

TODO: convert radalerts subpackage to using generic alerts class

Adding a new radiation alert:
    - edit alert.json file
    - modify get_message() method if needed
    - create <new>alerts.py (e.g. radalerts.py, dumpalerts.py) and
      add a new method to radpars.py (or create dumpspar.py in the
      future) which will fetch the current value/data for verification

Disabling a radiation alert:
    - touch <name>.log in the working directory to disable alerts for
      24 hours or extend the default 24h time period during which an
      alert is disabled after being triggered
    - or edit alerts.json and change manual_disable from 0 to 1.
"""
import os
import time
#: Formatting
from pprint import pformat
from email.message import EmailMessage
from subprocess import Popen, PIPE

class Alert(object):
    """
    Base Alert class
    """
    def __init__(self,
                 mode,
                 name,
                 email,
                 action,
                 check_func,
                 message='',
                ):
        self.mode = mode
        self.name = name
        #: TODO Must refine names of log / lock files for alerts if one desgined
        #: alert could have multiple states (i.e. warning_hi then caution_hi for and MSID temp)
        self.logfile = f"{name}.log"
        self.email = email
        self.action = action
        self.check_func = check_func
        self.set_subject()
        self.set_message(message)

    def set_subject(self):
        if self.mode == 'test':
            self.subject = f'TEST {self.name}'
        else:
            self.subject = self.name
    
    def set_message(self,_message):
        #: Wrap email message content with uniform content.
        _content = f"{self.name} Violation Occured\n"
        _content += f"{_message}\n"
        _content += f"{self.action}\n"
        _content += f"{os.environ.get('USER')}@{os.environ.get('HOST')}"
        self.message = _content
    

    def check(self, **check_kwargs):
        """
        Run the alert's check function to determine trigger, message, and send alert.
        """
        _is_triggered, _message = self.check_func(**check_kwargs)
        if _is_triggered:
            self.set_message(_message)
            if os.path.exists(self.logfile):
                remove_after_24h(self.logfile)
            else:
                with open(self.logfile, "w") as fh:
                    fh.write(self.message)
                self.send_alert()



    def send_alert(self):
        """
        Use attributes to send alert notification.
        """
        msg = EmailMessage()

        msg["From"] = "MTA"
        msg['To'] = self.email
        msg['Subject'] = self.subject
        msg.set_content(self.message)
        p = Popen(["/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        (out, error) = p.communicate(msg.as_bytes())

    def __repr__(self):
        return (' '.join([f'<{self.__class__.__name__}:',
                          f'mode={self.mode}',
                          f'email={self.email}',
                          f'logfile={self.logfile}',
                          f'name={self.name}>']))


    def __str__(self):
        return pformat(self.__dict__)
    
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