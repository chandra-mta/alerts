"""
Functions for determining alert triggers

:NOTE: Alert functions are custom algorithms as needed for determining if an alert should trigger,
    or what the notification message should be. As such, they are scoped outside of an Alert class instance.
    This means that all Alert instance attributes of importance in teh check must be passed to
    the function as a keyword argument.

"""

TRIGGER_SEQUENCE = (
    pcadmode,
    fmt,
) #: Tuple of Function handles to run for checking all the satalerts.

def pcadmode(data):
    """
    Include Comm Information?
    """
    message = f"Chandra realtime telemetry shows PCADMODE {data.get('value')} at {data.get('cxotime')}\n"
    if data.get('value') == "NSUN":
        is_triggered = True
    else:
        is_triggered = False
    return is_triggered, message

def fmt(sat_dataset):
    pass

def run_all_satalerts():
    pass