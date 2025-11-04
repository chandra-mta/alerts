"""
Functions for determining alert triggers

:Check Functions: Alerts are instatiated with a check function to handle the individual algorithmic
    calculations needed to record the trigger of an alert, or edit the notification of a

"""
import os
from cxotime import CxoTime

def delay(instance, step):
    """
    Increment or decrement the delay count of alert instance by pos. or neg. step.
    If delay count satisfies limit, nullify count and trigger alert.

    All delay counts operate within a range of [0, delay_limit -1] and mark the alert as triggered.
    If the delay count reaches zero again and the alert is stored as alerting, the log file is cleared.
    """
    instance.delay_count += step
    if instance.delay_count >= instance.delay_limit:
        #: Record alert trigger. Alert notification will handle log file creation.
        instance.is_triggered = True
        instance.delay_count = instance.delay_limit - 1
    elif instance.delay_count <= 0:
        #: Alert nullified. Delete log file if one exists.
        if os.path.exists(instance.logfile):
            os.remove(instance.logfile)
        instance.delay_count = 0
    #: Otherwise, proceed with delay count stepped as normal.

#
# --- Trigger algorithm functions for alert instances. Pass as check_func attribute,
# --- and ensure function operates on native alert instance attributes.
#

def pcadmode(instance, aopcadmd):
    """
    Checks AOPCADMD MSID for violation od PCAD MODE

    TODO Include Comm Information?
    """
    instance.message = f"Chandra realtime telemetry shows PCADMODE {aopcadmd.get('value')} at {CxoTime(aopcadmd.get('cxotime')).date}\n"
    if aopcadmd.get('value') == "NSUN":
        delay(instance, 1) #: Increment Delay Counter
    else:
        delay(instance, -1) #: Decrement Delay Counter

def fmt(sat_dataset):
    pass

def run_all_satalerts():
    pass