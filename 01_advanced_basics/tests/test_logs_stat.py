import unittest
import json
import os
import sys
import shutil
from datetime import datetime
from statistics import mean, median

sys.path.append(os.path.realpath('.'))

from src import (
    get_logs_stat, get_url_stats
)

class TestLogsStat(unittest.TestCase):
    def setUp(self):
        self.log_processed = {
            'url1': [1, 1, 1],
            'url2': [1, 1, 1],
        }
        self.stats = {}
        for log in self.log_processed:
            requests_times = self.log_processed[log]
            self.stats[log] = {
                'url': log,
                'count': len(requests_times),
                'count_perc': None,
                'time_sum': sum(requests_times),
                'time_perc': None,
                'time_avg': mean(requests_times),
                'time_max': max(requests_times),
                'time_med': median(requests_times)
            }
    
    def test_stats_per_url(self):
        for url_stat in get_url_stats(self.log_processed):
            self.assertDictEqual(url_stat, self.stats[url_stat['url']])


if __name__ == '__main__':
    unittest.main()
