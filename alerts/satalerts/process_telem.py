# Licensed under a 3-clause BSD style license - see LICENSE
"""
Internal module for processing an acron telemetry table into pythonic alert classes.
"""
def reorient_telemetry(telem_table):
    """
    Reorient a telemetry astropy table into a hash-table of the most recent msid values.
    """
    _msids = [_ for _ in telem_table.columns if _ != "TIME"]
    dataset = {}
    _row = telem_table[-1]
    for _msid in _msids:
        dataset[_msid] = {'cxotime': _row['TIME'], 'value': _row[_msid]}
    return dataset