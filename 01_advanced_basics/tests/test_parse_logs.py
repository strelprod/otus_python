import unittest
import os
import sys
import shutil
from datetime import datetime

sys.path.append(os.path.realpath('.'))

from src import (
    parsing_log, process_log,
    LOG_NGINX_REGEX, LOG_NGINX_LINE
)

<<<<<<< HEAD

=======
>>>>>>> 96580ef... upd test name for parse logs nginx
LOGS_NGINX_FOR_TEST = """
1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390
1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.133
1.169.137.128 -  - [29/Jun/20" "-" "1498697422-2118016444-4708-9752769" "712e90144abee9" 0.199
1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "-" "Lynx/2.8.8d-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752745" "2a828197ae235b0b3cb" 0.704
"""

class TestParseNginxLogs(unittest.TestCase):
    def setUp(self):
        self.log_fname = 'logs_testing_parse.log'
        self.opened_log_file = open(self.log_fname, 'a+', encoding='utf-8')
        self.opened_log_file.write(LOGS_NGINX_FOR_TEST)
        self.parsed_data = [
            ("/api/v2/banner/25019354", 0.390),
            ("/api/1/photogenic_banners/list/?server_name=WIN7RB4 ", 0.133),
            (None, None),
            (None, None),
        ]

    def tearDown(self):
        self.opened_log_file.close()
        os.remove(self.log_fname)

    def test_parse_log_file(self):
        for i, row in enumerate(parsing_log(self.opened_log_file, LOG_NGINX_LINE)):
            self.assertEqual(row, self.parsed_data[i])


if __name__ == '__main__':
    unittest.main()
