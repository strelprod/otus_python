#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';


import argparse
import re
from datetime import datetime
from src import (
    prepare_config, find_last_logfile,
    is_report_exists, process_log,
    get_logs_stat, save_report
)


LOG_FILE_REGEX = r'nginx-access-ui\.log-([0-9]{8})(\.gz|$)'
LOG_FILE_PAT = re.compile(LOG_FILE_REGEX)
LOG_NGINX_REGEX = r'\"(GET|POST|HEAD|PUT|DELETE|CONNECT|OPTIONS|TRACE|PATCH)' \
                  r' (.+) (HTTP|http)\/\d+\.\d\".+(\d\.\d+)$'
LOG_NGINX_PAT = re.compile(LOG_NGINX_REGEX)
REPORT_TPL = "report-{}.html"


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def parse_inpurt_args():
    parser = argparse.ArgumentParser(description='Process logs')
    parser.add_argument('--config', action="store", dest="config", 
                        default='', type=str,
                        help='input config in json format')
    args = parser.parse_args()
    return args


def main():
    try:
        print("Start main")
        inpurt_args = parse_inpurt_args()
        config_prepared = prepare_config(config, inpurt_args.config)
        if not config_prepared:
            return
        print("Done config_prepared")
        log_file_data = find_last_logfile(config_prepared['LOG_DIR'], 
                                          LOG_FILE_PAT)
        print("Done find_last_logfile")
        if log_file_data:
            dt = datetime.strftime(log_file_data.dt, '%Y.%m.%d')
            report_fname = REPORT_TPL.format(dt)
            if is_report_exists('./reports', report_fname):
                print("Report already exists")
                return
            log_processed = process_log(log_file_data, LOG_NGINX_PAT)
            print("Done process_log")
            if not log_processed:
                return
            logs_stat = get_logs_stat(log_processed, 
                                      config_prepared['REPORT_SIZE'])
            print("Done get_logs_stat")
            if save_report(config_prepared['REPORT_DIR'], 
                           report_fname, 
                           logs_stat):
                print("Done save_report")
            else:
                print("Failed save_report")
        else:
            print("Logs not found")
            return
    except BaseException as e:
        print(f"unknown exception: {str(e)}")
    else:
        print("End main")
    return
    

if __name__ == "__main__":
    main()
