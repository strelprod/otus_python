import logging
import re
from .config import prepare_config
from .find_logs import (
    find_last_logfile, parse_log_file_name,
    get_logfiles, LogFileData
)
from .logs_stat import get_logs_stat, get_url_stats
from .parse_log import process_log
from .report import is_report_exists, save_report


LOG_FORMAT = "[%(asctime)s] %(levelname).1s %(message)s"
LOG_FORMATTER = logging.Formatter(LOG_FORMAT)
LOG_FILE_REGEX = r'nginx-access-ui\.log-([0-9]{8})(\.gz|$)'
LOG_FILE_PAT = re.compile(LOG_FILE_REGEX)
LOG_NGINX_REGEX = r'\"(GET|POST|HEAD|PUT|DELETE|CONNECT|OPTIONS|TRACE|PATCH)' \
                  r' (.+) (HTTP|http)\/\d+\.\d\".+(\d\.\d+)$'
LOG_NGINX_PAT = re.compile(LOG_NGINX_REGEX)
REPORT_TPL = "report-{}.html"
CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}
