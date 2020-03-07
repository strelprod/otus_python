import unittest
import json
import os
import sys
import shutil
from datetime import datetime

sys.path.append(os.path.realpath('.'))

from src import (
    is_report_exists, save_report
)

class TestReport(unittest.TestCase):
    def setUp(self):
        self.report_path = "test_report_dir"
        if not os.path.exists(self.report_path):
            os.makedirs(self.report_path)
        self.reports = [
            'report_1.html',
            'report_2.html'
        ]
        for fname in self.reports:
            fpath = os.path.join(self.report_path, fname)
            with open(fpath, 'w+', encoding='utf-8') as report:
                report.write('')

    def tearDown(self):
        shutil.rmtree(self.report_path)
    
    def test_existing_reports(self):
        check = is_report_exists(self.report_path, self.reports[0])
        self.assertTrue(check)
        check = is_report_exists(self.report_path, "fake_rep.html")
        self.assertFalse(check)

    def test_save_report(self):
        save_res = save_report(self.report_path, 'new_report.html', {})
        fpath = os.path.join(self.report_path, 'new_report.html')
        is_file_exists = os.path.exists(fpath)
        self.assertEqual(save_res, is_file_exists)


if __name__ == '__main__':
    unittest.main()
