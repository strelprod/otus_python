#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import argparse
from src import (
    prepare_config, find_last_logfile, get_report_fname,
    process_log, get_logs_stat, save_report
)
import json


LOG_FORMAT = "[%(asctime)s] %(levelname).1s %(message)s"
LOG_FORMATTER = logging.Formatter(LOG_FORMAT)


logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt='%Y.%m.%d %H:%M:%S',
                    filename=None)


def set_logger_file(conf, log_formatter=LOG_FORMATTER):
    if "LOGGER_FILE" in conf:
        try:
            root_logger = logging.getLogger()
            file_handler = logging.FileHandler(conf['LOGGER_FILE'])
            file_handler.setFormatter(log_formatter)
            root_logger.addHandler(file_handler)
        except FileNotFoundError:
            msg = "Logger_file using in config not found: {}"
            logging.error(msg.format(conf['LOGGER_FILE']))
            raise FileNotFoundError(msg.format(conf['LOGGER_FILE']))
    else:
        logging.info("LOGGER_FILE is not in config, logging to stdout")


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
        logging.info("Done parse_inpurt_args")
        config_prepared = prepare_config(inpurt_args.config)
        logging.info("Done config_prepared")
        set_logger_file(config_prepared)
        log_file_data = find_last_logfile(config_prepared['LOG_DIR'])
        logging.info("Done find_last_logfile")
        if log_file_data:
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
        else:
            logging.info("Exit: Logs not found")
    except (FileNotFoundError, json.decoder.JSONDecodeError,
            AssertionError, KeyError) as e:
        logging.exception(str(e))
    except BaseException:
        logging.exception("Unknown exception")


if __name__ == "__main__":
    main()
