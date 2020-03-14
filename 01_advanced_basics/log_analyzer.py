#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import argparse
from src import (
    prepare_config, find_last_logfile, get_report_fname,
    process_log, get_logs_stat, save_report
)
import os


LOG_FORMAT = "[%(asctime)s] %(levelname).1s %(message)s"
LOG_FORMATTER = logging.Formatter(LOG_FORMAT)
DEFAULT_CONFIG_PATH = './config.json'


logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt='%Y.%m.%d %H:%M:%S',
                    filename=None)


def set_logger_file(logger_fpath):
    if logger_fpath:
        log_dir = os.path.split(logger_fpath)[0]
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        root_logger = logging.getLogger()
        file_handler = logging.FileHandler(logger_fpath)
        file_handler.setFormatter(LOG_FORMATTER)
        root_logger.addHandler(file_handler)
    else:
        logging.info("LOGGER_FILE is not in config, logging to stdout")


def parse_inpurt_args():
    parser = argparse.ArgumentParser(description='Process logs')
    parser.add_argument('--config', action="store", dest="config",
                        default=DEFAULT_CONFIG_PATH, type=str,
                        help='input config in json format')
    args = parser.parse_args()
    return args


def main():
    try:
        inpurt_args = parse_inpurt_args()
        logging.info("Done parse_inpurt_args")
        
        config_prepared = prepare_config(inpurt_args.config)
        logging.info("Done config_prepared")

        set_logger_file(config_prepared.get('LOGGER_FILE'))

        log_file_data = find_last_logfile(config_prepared['LOG_DIR'])
        logging.info("Done find_last_logfile")

        if not log_file_data:
            logging.info("Exit: Logs not found")
            return

        report_fname = get_report_fname(config_prepared['REPORT_DIR'],
                                        log_file_data.dt)
        logging.info("Done get_report_fname")

        log_processed = process_log(log_file_data)
        logging.info("Done process_log")

        logs_stat = get_logs_stat(log_processed,
                                    config_prepared['REPORT_SIZE'])
        logging.info("Done get_logs_stat")

        save_report(config_prepared['REPORT_DIR'],
                    report_fname,
                    logs_stat)
        logging.info("Done save_report")
    except:
        logging.exception('Exception')


if __name__ == "__main__":
    main()
