#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import argparse
from datetime import datetime
from src import (
    prepare_config, find_last_logfile, is_report_exists,
    process_log, get_logs_stat, save_report,
    CONFIG, LOG_FILE_PATH, LOG_NGINX_LINE, 
    REPORT_TPL
)
import json


LOG_FORMAT = "[%(asctime)s] %(levelname).1s %(message)s"
LOG_FORMATTER = logging.Formatter(LOG_FORMAT)


logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt='%Y.%m.%d %H:%M:%S',
                    filename=None)


def parse_inpurt_args():
    parser = argparse.ArgumentParser(description='Process logs')
    parser.add_argument('--config', action="store", dest="config",
                        default='./config.json', type=str,
                        help='input config in json format')
    args = parser.parse_args()
    return args


def main():
    try:
        inpurt_args = parse_inpurt_args()
        logging.debug("Done parse_inpurt_args")
        config_prepared = prepare_config(CONFIG,
                                         inpurt_args.config,
                                         LOG_FORMATTER)
        logging.debug("Done config_prepared")
        log_file_data = find_last_logfile(config_prepared['LOG_DIR'],
                                          LOG_FILE_PATH)
        logging.debug("Done find_last_logfile")
        if log_file_data:
            dt = datetime.strftime(log_file_data.dt, '%Y.%m.%d')
            report_fname = REPORT_TPL.format(dt)
            if is_report_exists(config_prepared['REPORT_DIR'], report_fname):
                logging.info(f"Exit: Report {report_fname} already exists")
                return
            log_processed = process_log(log_file_data, LOG_NGINX_LINE)
            logging.debug("Done process_log")
            
            logs_stat = get_logs_stat(log_processed,
                                      config_prepared['REPORT_SIZE'])
            logging.debug("Done get_logs_stat")
            save_report(config_prepared['REPORT_DIR'],
                        report_fname,
                        logs_stat)
            logging.info("Done save_report")
        else:
            logging.info("Exit: Logs not found")
    except (FileNotFoundError, json.decoder.JSONDecodeError,
            AssertionError, KeyError) as e:
        logging.exception(str(e))
    except BaseException:
        logging.exception("Unknown exception")


if __name__ == "__main__":
    main()
