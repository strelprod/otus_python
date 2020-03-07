import gzip
import logging


def parsing_log(file_obj, log_nginx_pat):
    while True:
        file_content = file_obj.readline()
        if not file_content:
            break
        parse_line = log_nginx_pat.search(file_content)
        try:
            url = parse_line.group(2)
            request_time = parse_line.group(4)
        except AttributeError:
            yield None, None
        else:
            yield url, float(request_time)


def process_log(log_data, log_nginx_pat):
    allowed_errors_proc = 0.1
    total_lines = 0
    error_parse_line = 0
    log_processed = {}

    try:
        open_log = gzip.open if log_data.file_type == '.gz' else open
        log_file = open_log(log_data.file_path, 'rt', encoding='utf-8')
    except OSError:
        logging.error(f"Log file not found: {log_data.file_path}")
        return

    for url, request_time in parsing_log(log_file, log_nginx_pat):
        total_lines += 1
        if url and request_time:
            if url not in log_processed:
                log_processed[url] = [request_time]
            else:
                log_processed[url].append(request_time)
        else:
            error_parse_line += 1
    log_file.close()
    if total_lines == 0 or \
       ((error_parse_line / total_lines) > allowed_errors_proc):
        err_txt = "Failed proccess logs: total " \
                  "lines={}, errors={}, allowed_proc={}"
        logging.error(err_txt.format(total_lines,
                      error_parse_line,
                      allowed_errors_proc))
        return {}
    return log_processed
