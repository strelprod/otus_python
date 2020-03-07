import unittest
import json
import os
import sys
import shutil
from datetime import datetime

sys.path.append(os.path.realpath('.'))

from src import (
    parse_log_file_name, find_last_logfile, 
    LOG_FILE_PAT, LogFileData
)

class TestFindLogs(unittest.TestCase):
    def setUp(self):
        self.logs_path = "test_logs_dir"
        if not os.path.exists(self.logs_path):
            os.makedirs(self.logs_path)
        self.log_files = [
            'nginx-access-ui.log-20170630',
            'nginx.log-20170630'
        ]
        for fname in self.log_files:
            fpath = os.path.join(self.logs_path, fname)
            with open(fpath, 'w+', encoding='utf-8') as log:
                log.write('')

    def tearDown(self):
        shutil.rmtree(self.logs_path)

    def test_parse_log_file_name(self):
        parsed = parse_log_file_name(self.log_files[0], LOG_FILE_PAT)
        real = (self.log_files[0], '20170630', '')
        self.assertEqual(parsed, real)
        parsed = parse_log_file_name(self.log_files[1], LOG_FILE_PAT)
        self.assertEqual(parsed, ())
    
    def test_find_last_logfile(self):
        filepath = os.path.join(self.logs_path, self.log_files[0])
        dt = datetime.strptime('20170630', '%Y%m%d')
        parsed = find_last_logfile(self.logs_path, LOG_FILE_PAT)
        self.assertEqual(parsed, LogFileData(filepath, dt, ''))


if __name__ == '__main__':
    unittest.main()
