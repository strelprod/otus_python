from datetime import datetime
from collections import namedtuple
import os
import re


LogFileData = namedtuple('Log_file', ['file_path', 'dt', 'file_type'])
LOG_FILE_REGEX = r'nginx-access-ui\.log-(\d{8})(\.gz|$)'
LOG_FILE_PATH = re.compile(LOG_FILE_REGEX)


def parse_log_file_name(fname, log_file_path):
    parsed = log_file_path.search(fname)
    if parsed:
        return parsed.group(0), parsed.group(1), parsed.group(2)


def get_logfiles(logs_dir, log_file_path):
    for path, _, files in os.walk(logs_dir):
        for fname in files:
            parsed = parse_log_file_name(fname, log_file_path)
            if not parsed:
                continue
            filepath = os.path.join(path, parsed[0])
            dt = datetime.strptime(parsed[1], '%Y%m%d')
            ftype = parsed[2]
            yield filepath, dt, ftype


def find_last_logfile(logs_dir, log_file_path=LOG_FILE_PATH):
    log_file_data = None
    for data in get_logfiles(logs_dir, log_file_path):
        if not log_file_data or data[1] > log_file_data.dt:
            log_file_data = LogFileData(data[0], data[1], data[2])
    return log_file_data
