#!/usr/bin/env /proj/sot/ska3/flight/bin/python

"""
Read the most recent radiation parameters from a local source
"""

import os
import sys
import numpy as np
from cxotime import CxoTime
import tables

ALLOWED_MODES = ("test", "flight")

HOME = os.environ.get('HOME')

#ARC_PATH = '/proj/sot/ska3/flight/data/arc'
ARC_PATH = f"{HOME}/git/radalerts/test-data"
ACE_H5 = f"{ARC_PATH}/ACE.h5"
HRC_SHIELD_H5 = f"{ARC_PATH}/hrc_shield.h5"


def get_ace_p3(path=ACE_H5):
    """
    Read arc ACE.h5 file, check if there are nominal p3 data
    in the last 12h and compute the 2-hour p3 fluence
    """

    # ACE
    try:
        with tables.open_file(path, mode='r',
                              filters=tables.Filters(complevel=5, complib='zlib')) as h5:
            table = h5.root.data
            time = table.col('time')
            p3 = table.col('p3')

            # nominal ACE P3 entries in the last 12h
            ok = (time > CxoTime().secs - 12 * 3600) & (p3 > 0)
            if len(p3[ok]) > 0:
                status = True
            else:
                status = False

            # compute the 2-hour p3 fluence
            ok = (time > CxoTime().secs - 2 * 3600) & (p3 > 0)
            if len(p3[ok]) > 0:
                fluence = np.median(p3[ok]) * 2 * 3600
            else:
                fluence = None

            h5.root.data.flush()

    except (OSError, IOError, tables.NoSuchNodeError):
        print("Warning: ACE data file not found, exiting")
        sys.exit(0)

    return {'ace_12h_status': status,
            'acep3_2h_fluence': fluence}


def get_hrc_shield_proxy(path=HRC_SHIELD_H5):
    """
    Read arc hrc_shield.h5 file, get the most recent value
    of the goes hrc shield proxy
    """

    # HRC shield proxy
    try:
        with tables.open_file(path, mode='r',
                              filters=tables.Filters(complevel=5, complib='zlib')) as h5:
            table = h5.root.data
            hrc_shield = table.col('hrc_shield')[-1]
            lasttime = table.col('time')[-1]
            h5.root.data.flush()

            # GOES data comes every 5 min
            if lasttime < CxoTime().secs - 20 * 60:
                print(CxoTime(lasttime).date)
                print("Warning: No recent GOES data, data older than 20 min")
                sys.exit(0)

    except (OSError, IOError, tables.NoSuchNodeError):
        print("Warning: GOES data file not found, exiting")
        sys.exit(0)

    return hrc_shield





