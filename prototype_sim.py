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

def run_alert_check():
    pass

if __name__ == "__main__":
    #: Determine Config Section
    args = get_options()
    config = load_config(args.mode)
    #: can I edit the config temporarily?
    #config['TELEMETRY_FILES_DIR'] = os.getcwd()
    for k,v in config.items():
        print(k,v)
    current = alerts.satalerts.telemetry.get_tl_files(config)
    print(current)