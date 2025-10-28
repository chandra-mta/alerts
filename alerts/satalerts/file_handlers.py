# Licensed under a 3-clause BSD style license - see LICENSE
"""
Internal module for handling intermediate files storing spacecraft data,
and logging the status of alerting
"""
import os
import glob
from datetime import datetime
import core
from numpy.ma import masked
from astropy.table import Table

def _read(file):
    #: Read in entire text content to minimize I/O operation time
    with open(file) as f:
        content = f.read()
    return content

def _coerce(x):
    if isinstance(x,list):
        return [_coerce(_) for _ in x]
    elif isinstance(x,str):
        #: String parsing.
        x = x.strip()
        if x == '':
            return masked
        #: If numeric, convert
        try:
            return int(x)
        except ValueError:
            try:
                return float(x)
            except ValueError:
                return x
    else:
        return x
    
def _parse(content):
    raw_lines = [line for line in content.split("\n")]
    #: Headers are written with an additional tab character at the end.
    header = raw_lines[0].strip().split('\t')
    #: Cannot strip the actual data lines in case the final column value is empty string, meaning masked value.
    data = _coerce([line.split('\t') for line in raw_lines[2:] if line != ''])
    return header, data

def _format(header, data):
    column_number = len(header)
    #: Drop non-matching rows and log
    rows = []
    for idx, entry in enumerate(data):
        if len(entry) != column_number:
            #: TODO Insert logging for handling ill-written telemetry files
            raise Exception(f"{header}, {entry}, {idx}")
        row = {}
        for i,j in zip(header,entry):
            row[i] = j
        rows.append(row)
    return Table(rows=rows)

def read_telemetry_file(file):
    """
    Read the acorn-formatted telemetry file into an astropy table
    """
    content = _read(file)
    header, data = _parse(content)
    table = _format(header, data)
    return table

def _find_tl_files(CONFIG):
    _list = glob.glob(f"{CONFIG.get('TELEMETRY_FILES_DIR')}/chandra*.tl")
    #: If multiple for each category exist, then remove the preceding files if configured to do so.
    current = {}
    preceding = {}
    for _file in _list:
        _category = _file.split("_")[0].split('chandra')[1]
        _previous_file = current.get(_category)
        if _previous_file is None:
            #: Not been identified yet.
            current[_category] = _file
        else:
            #: Identified before, so check for latest
            if os.path.getmtime(_previous_file) < os.path.getmtime(_file):
                preceding[_category] = _previous_file
                current[_category] = _file
            else:
                preceding[_category] = _file
    return current, preceding

def _select_tl_files(current):
    process = {}
    stale = {}
    _now = datetime.now().timestamp()
    for _category, _file in current.items():
        print(_file, _now - os.path.getmtime(_file))
        if (_now - os.path.getmtime(_file)) <= core.STALE_THRESHOLD:
            process[_category] = _file
        else:
            stale[_category] = _file
    return process, stale

def get_tl_files(CONFIG):
    """
    Use package-approved configuration to handle available telemetry files
    """
    current, preceding = _find_tl_files(CONFIG)

    if CONFIG.getboolean('DELETE_PRECEDING'):
        for _file in preceding.values():
            if os.path.exists(_file):
                os.system(f"rm {_file}")
    
    if CONFIG.getboolean("EXCLUDE_STALE"):
        process, stale  = _select_tl_files(current)
        return process
    else:
        return current
