#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import argparse
import re
from datetime import datetime
from src import (
    prepare_config, find_last_logfile, is_report_exists, 
    process_log, get_logs_stat, save_report, 
    CONFIG, LOG_FORMATTER, LOG_FORMAT,
    LOG_FILE_PAT, LOG_NGINX_PAT, REPORT_TPL
)


logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt='%Y.%m.%d %H:%M:%S',
                    filename=None)


def parse_inpurt_args():
    parser = argparse.ArgumentParser(description='Process logs')
    parser.add_argument('--config', action="store", dest="config",
                        default='', type=str,
                        help='input config in json format')
    args = parser.parse_args()
    return args


def main():
    try:
        inpurt_args = parse_inpurt_args()
        config_prepared = prepare_config(CONFIG, 
                                         inpurt_args.config,
                                         LOG_FORMATTER)
        if not config_prepared:
            return
        logging.debug("Done config_prepared")
        log_file_data = find_last_logfile(config_prepared['LOG_DIR'],
                                          LOG_FILE_PAT)
        logging.debug("Done find_last_logfile")
        if log_file_data:
            dt = datetime.strftime(log_file_data.dt, '%Y.%m.%d')
            report_fname = REPORT_TPL.format(dt)
            if is_report_exists(config_prepared['REPORT_DIR'], report_fname):
                logging.info(f"Report {report_fname} already exists")
                return
            log_processed = process_log(log_file_data, LOG_NGINX_PAT)
            logging.debug("Done process_log")
            if not log_processed:
                return
            logs_stat = get_logs_stat(log_processed,
                                      config_prepared['REPORT_SIZE'])
            logging.debug("Done get_logs_stat")
            if save_report(config_prepared['REPORT_DIR'],
                           report_fname,
                           logs_stat):
                logging.debug("Done save_report")
            else:
                logging.error("Failed save_report")
        else:
            logging.info("Logs not found")
    except BaseException:
        logging.exception("Unknown exception")
    return


if __name__ == "__main__":
    main()
