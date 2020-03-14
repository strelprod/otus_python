import gzip
import logging
import re


LOG_NGINX_REGEX = r'\"(GET|POST|HEAD|PUT|DELETE|CONNECT|OPTIONS|TRACE|PATCH)' \
                  r' (.+) (HTTP|http)\/\d+\.\d\".+(\d\.\d+)$'
LOG_NGINX_LINE = re.compile(LOG_NGINX_REGEX)


def parsing_log(file_obj, log_nginx_line):
    while True:
        file_content = file_obj.readline()
        if not file_content:
            break
        parse_line = log_nginx_line.search(file_content)
        try:
            url = parse_line.group(2)
            request_time = parse_line.group(4)
        except AttributeError:
            yield None, None
        else:
            yield url, float(request_time)


def verify_allowed_errors(total_lines, 
                          error_parse_line, 
                          allowed_errors_proc):
    errors_proc = error_parse_line / total_lines
    if (total_lines == 0) or (errors_proc > allowed_errors_proc):
        err_txt = "Failed proccess logs: total " \
                  "lines={}, errors={}, allowed_proc={}"
        logging.error(err_txt.format(total_lines,
                      error_parse_line,
                      allowed_errors_proc))
        raise AssertionError(err_txt.format(total_lines,
                                            error_parse_line,
                                            allowed_errors_proc))


def process_log(log_data, 
                log_nginx_line=LOG_NGINX_LINE, 
                allowed_errors_proc=0.1):
    total_lines = 0
    error_parse_line = 0
    log_processed = {}

    try:
        open_log = gzip.open if log_data.file_type == '.gz' else open
        log_file = open_log(log_data.file_path, 'rt', encoding='utf-8')
    except FileNotFoundError:
        logging.error(f"Log file not found: {log_data.file_path}")
        raise FileNotFoundError(f"Log file not found: {log_data.file_path}")

    for url, request_time in parsing_log(log_file, log_nginx_line):
        total_lines += 1
        if url and request_time:
            if url not in log_processed:
                log_processed[url] = [request_time]
            else:
                log_processed[url].append(request_time)
        else:
            error_parse_line += 1
    log_file.close()
    verify_allowed_errors(total_lines, 
                          error_parse_line, 
                          allowed_errors_proc)
    return log_processed
