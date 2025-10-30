"""
pytest -s tests/test_basic.py --email <test_mailing_list>
pytest -s tests/test_basic.py::<method> --email <test_mailing_list>

The tests email defaults to mtadude@cfa.harvard.edu without
the --email option(see conftest.py)
"""

import numpy as np
import os
import time
from astropy.table import Table, Column
from ..alerts import *
from ..radpars import *

TESTMODE = 'test'

# RadAlerts with violations
RADALERTS = [{"name": "bool",
              "type": "bool",
              "category": "warning",
              "lo": 0,
              "hi": 0,
              "triggered": 0,
              "blackout_tstart": 24,
              "blackout_tstop": 8,
              "manual_disable": 0,
              "val": 0.0,
              "action": "Action 1",
              "url": "https://bool.com"
             },
             {
              "name": "upper_caution",
              "type": "upper",
              "category": "caution",
              "lo": 0,
              "hi": 1.0e7,
              "triggered": 0,
              "blackout_tstart": 24,
              "blackout_tstop": 5,
              "manual_disable": 0,
              "val": 3.0e7,
              "action": "Action 2",
              "url": "htpps://upper_caution.com"
             },
             {
              "name": "upper_warning",
              "type": "upper",
              "category": "warning",
              "lo": 0,
              "hi": 1.0e8,
              "triggered": 0,
              "blackout_tstart": 24,
              "blackout_tstop": 5,
              "manual_disable": 0,
              "val": 1.0e9,
              "action": "Action 2",
              "url": "htpps://upper_warning.com"
             },
             {
              "name": "lower_caution",
              "type": "lower",
              "category": "caution",
              "lo": 20.0,
              "hi": 0,
              "triggered": 0,
              "violation_type": '',
              "blackout_tstart": 24,
              "blackout_tstop": 0,
              "manual_disable": 0,
              "val": 15.0,
              "action": "Action 3",
              "url": "https://lower_caution.com"
             },
             {
              "name": "lower_warning",
              "type": "lower",
              "category": "warning",
              "lo": 10.0,
              "hi": 0,
              "triggered": 0,
              "violation_type": '',
              "blackout_tstart": 24,
              "blackout_tstop": 0,
              "manual_disable": 0,
              "val": 5.0,
              "action": "Action 3",
              "url": "https://lower_warning.com"
             },
             {
              "name": "range_warning_lo",
              "type": "range",
              "category": "warning",
              "lo": 10.0,
              "hi": 20.0,
              "triggered": 0,
              "violation_type": '',
              "blackout_tstart": 24,
              "blackout_tstop": 0,
              "manual_disable": 0,
              "val": 7.0,
              "action": "Action 4",
              "url": "https://range_warning.com/lo"
             },
             {
              "name": "range_warning_hi",
              "type": "range",
              "category": "warning",
              "lo": 5.0,
              "hi": 25.0,
              "triggered": 0,
              "violation_type": '',
              "blackout_tstart": 24,
              "blackout_tstop": 0,
              "manual_disable": 0,
              "val": 28.0,
              "action": "Action 5",
              "url": "https://range_warning.com/hi"
             }]


def test_alert_object(email):

    alert = RadAlert(mode=TESTMODE,
                  name='test_alert_object',
                  type_="lower",
                  category="caution",
                  val=10,
                  lo=5,
                  hi=15,
                  url='https://test.com/ace',
                  email=email,
                  action='Action test',
                  violation_type='caution_lo')
    
    assert alert.logfile == f"{alert.name}_{alert.category}.log"
    assert alert.subject == f"TEST {alert.name}"
    assert alert.message == f"""{alert.name} violation occured ({alert.violation_type})
Value: {alert.val:.1e}
Lo limit: {alert.lo:.1e}
{alert.action}
This message sent to {alert.email}
"""


def test_trigger_alerts():
    """
    """
    alerts = Table(RADALERTS)

    assert np.all([not a['triggered'] for a in alerts])
    
    for a in alerts:
        print(a['name', 'val'])
        a = trigger_alerts(a)

    assert np.all([a['triggered'] for a in alerts])


def test_send_alert_1(email):
    """
    Test that new alerts are sent (new = no existing logfiles)
    Expected result: emails for each alert received
                     and logfiles created.
    """

    alerts = Table(RADALERTS)

    for a in alerts:
        
        logfile = f"{a['name']}_{a['category']}.log"
        if os.path.exists(logfile):
            os.remove(logfile)

        a = trigger_alerts(a)
        send_alert(a, mode=TESTMODE, email=email)

    assert np.all([os.path.exists(logfile) for a in alerts])


def test_send_alert_2(email):
    """
    Test that alerts are blocked if logfiles exist. If emails with
    subject "TEST {subject}" are recieved then the test has failed.
    """

    alerts = Table(RADALERTS)
    alerts['subject'] = 'lockfile disable failed'

    for a in alerts:
        #a['subject'] = 'lockfile disable failed'
        send_alert(a, mode=TESTMODE, email=email)

    # Test that logfiles are "old" (here, older than 0.0005 sec)
    dts = []
    for a in alerts:
        logfile = f"{a['name']}_{a['category']}.log"
        dt = time.time() - os.path.getctime(logfile) # sec
        dts.append(dt)

    assert np.all([dt > 0.0005 for dt in dts])


def test_send_alert_3(email):
    """
    The send_alert routine is called twice in this test:
    1st time to test that logfiles are removed after 24h,
    2nd time to test that alerts are sent after removing old
    logfiles. Expected result: three emails received with
    subject 'after 24h' and new logfiles.
    """

    alerts = Table(RADALERTS)
    alerts['subject'] = 'after 24h'
    col = Column(name='logfile', data=[''] * len(alerts), dtype='S100')
    alerts.add_column(col)

    for a in alerts:
        # set timestamp of logfiles to 24h and 2 mins in the past
        t = time.time() - 24 * 3600 - 120
        stamp = time.strftime('%Y%m%d%H%M', time.localtime(t))
        a['logfile'] = f"{a['name']}_{a['category']}.log"
        os.system(f"touch -t {stamp} {a['logfile']}")
        send_alert(a, mode=TESTMODE, email=email) # removes logfiles

    # Test that logfiles are removed after 24h
    assert np.all([not os.path.exists(a['logfile']) for a in alerts])

    for a in alerts:
        send_alert(a, mode=TESTMODE, email=email) # sends new alerts

    # Test that logfiles are new, younger than 1 sec
    dts = []
    for a in alerts:
        dt = time.time() - os.path.getctime(a['logfile']) # sec
        dts.append(dt)

    assert np.all([dt < 1 for dt in dts])

    # Clean up
    for a in alerts:
        os.remove(a['logfile'])


def test_send_alert_4(email):
    """
    Test the 'manual_disable' option. Alter logfiles to be >24h old and
    set the 'manual_disable' property to 1 (True). Test that al alerts
    remain locked.
    """

    alerts = Table(RADALERTS)
    col = Column(name='logfile', data=[''] * len(alerts), dtype='S100')
    alerts.add_column(col)

    # Manually disable all alerts
    alerts['manual_disable'] = 1
    alerts['subject'] = 'manual disable failed'

    for a in alerts:
        t = time.time() - 30 * 3600 # 30h old logfile
        stamp = time.strftime('%Y%m%d%H%M', time.localtime(t))
        a['logfile'] = f"{a['name']}_{a['category']}.log"
                
        os.system(f"touch -t {stamp} {a['logfile']}")
        
        dt = time.time() - os.stat(a['logfile']).st_mtime # sec
        assert dt > 24 * 3600

        # removes logfiles if manual disable fails
        send_alert(a, mode=TESTMODE, email=email)

    # Clean up
    for a in alerts:
        if os.path.exists(a['logfile']):
            os.remove(a['logfile'])
