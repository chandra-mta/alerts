#!/proj/sot/ska3/flight/bin/python

"""
Run prototype of package for luke-v sim
"""
import alerts
import os
import argparse
from configparser import ConfigParser, ExtendedInterpolation
_CONFIGS = ConfigParser(interpolation = ExtendedInterpolation(), default_section='primary')
_CONFIGS.read('config.ini')

def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices = ['primary', 'secondary', 'buocc', 'test', 'sim'], required = True, help = "Determine configuration of script run.")
    return parser.parse_args()

def load_config(mode):
    config = _CONFIGS[mode]
    return config

def pull_tl_data(config):
    current = alerts.satalerts.telemetry.get_tl_files(config)
    #: Only testing the pcadmode and fmt alerts
    data = {}
    if current.get('PCAD') is not None:
        pcad_table = alerts.satalerts.telemetry.read_telemetry_file(current.get('PCAD'))
        pcad = alerts.satalerts.telemetry.latest_telem_value(pcad_table)
        data.update(pcad)
    if current.get('CCDM') is not None:
        ccdm_table = alerts.satalerts.telemetry.read_telemetry_file(current.get('CCDM'))
        ccdm = alerts.satalerts.telemetry.latest_telem_value(ccdm_table)
        data.update(ccdm)
    return data, current


def run_alert_check(config):
    delay_status = alerts.alerts.read_delay_status()
    data, current = pull_tl_data(config)
    action = "Check email for info.\nTelecon on 609-829-8540 PIN 132 194 285 : meet.google.com/fmc-gusj-eos\nA reminder, this may be connected to the voice loops at OCC\n"
    
    x = alerts.alerts.Alert(
        mode= 'sim',
        name = 'pcadmode',
        email = "william.aaron@cfa.harvard.edu",
        action = action,
        check_func = alerts.satalerts.trigger_satalerts.pcadmode,
        is_delayed = True,
        delay_count = delay_status.get('pcadmode').get('count'),
        delay_limit = delay_status.get('pcadmode').get('limit')
    )

    y = alerts.alerts.Alert(
        mode= 'sim',
        name = 'fmt',
        email = "william.aaron@cfa.harvard.edu",
        action = action,
        check_func = alerts.satalerts.trigger_satalerts.fmt
    )
    if data.get("AOPCADMD") is not None:
        x.check(aopcadmd = data["AOPCADMD"])
    if data.get("CCSDSTMF") is not None:
        y.check(ccsdstmf = data["CCSDSTMF"])

    alert_set = (x,y)
    alerts.alerts.write_delay_status(alert_set)

    # copy log files if they are present for examination since they are removed in regular processing
    
    if os.path.exists(x.logfile):
        if not os.path.exists(f"{x.logfile}~"):
            os.system(f"cp {current.get('PCAD')} ./")
            os.system(f"cp {x.logfile} {x.logfile}~")
    if os.path.exists(y.logfile):
        if not os.path.exists(f"{y.logfile}~"):
            os.system(f"cp {current.get('CCDM')} ./")
            os.system(f"cp {y.logfile} {y.logfile}~")


if __name__ == "__main__":
    #: Determine Config Section
    args = get_options()
    config = load_config(args.mode)
    #: Edit config option
    config['TELEMETRY_FILES_DIR'] = os.getcwd()
    run_alert_check(config)
    