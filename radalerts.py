#!/usr/bin/env /proj/sot/ska3/flight/bin/python

"""
Radiation monitoring for Chandra (GOES HRC proxy and ACE)
"""

import os
import numpy as np
import argparse
from .alerts import Alert
from .alerts import get_current_hour, trigger_alerts, send_alert
from .radpars import get_ace_p3, get_hrc_shield_proxy

ALLOWED_MODES = ("test", "flight")
TEST_EMAIL = "mtadude@cfa.harvard.edu"

HOME = os.environ.get('HOME')

#ARC_PATH = '/proj/sot/ska3/flight/data/arc'
ARC_PATH = f"{HOME}/git/radalerts/test-data"
ACE_H5 = f"{ARC_PATH}/ACE.h5"
HRC_SHIELD_H5 = f"{ARC_PATH}/hrc_shield.h5"


def get_options():
    """
    """
    parser = argparse.ArgumentParser(description='Chandra MTA radiation alerts')
    parser.add_argument('--email', type=str,
                        default=None,
                        help='Mailing list')
    parser.add_argument('--mode', type=str,
                        default='test',
                        help='Execution mode ("test", "flight")')
    args = parser.parse_args()
    return args


def main():
    """
    Check radiation violations
    """

    args = get_options()

    if args.mode not in ALLOWED_MODES:
        raise ValueError("Execution mode should be 'test' (default) or 'flight'")
    
    with open("alerts.json", "r") as fh:
        alerts = json.load(fh)

    # Radiation
    alerts = Table(alerts['radiation'])
    alerts['triggered'].dtype = bool
    col = Column(name='violation_type', data=[''] * len(alerts), dtype='S10')
    alerts.add_column(col)

    vals = {}
    
    # ACE
    ace = get_ace_p3(path=ARC_H5)
    for key in ace.keys():
        vals[key] = ace[key]

    # GOES HRC proxy
    vals['hrc_shield'] = get_hrc_shield_proxy(path=HRC_SHIELD_H5)

    for name in vals.keys():
        # expected keys are:
        # 'ace_12h_status', 'acep3_2h_fluence', 'hrc_shield'
        ok = alerts['name'] == name
        alerts['val'][ok] = vals[name]
    
    t = get_current_hour()

    for a in alerts:

        a = trigger_alerts(a)

        if a['triggered'] & (t > a['blackout_tstop']) & (t < a['blackout_tstart']) & (not a['manual_disable']):
            if arg.mode == 'test':
                if args.email is None:
                    email = TEST_EMAIL
                else:
                    email = args.email
            else:
                email = a.email
            send_alert(a, mode=args.mode, email=email)


if __name__ == "__main__":

    main()
