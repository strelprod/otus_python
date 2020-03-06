from statistics import mean, median


def get_logs_stat(log_processed, limit=None):
    stats = []
    total_count = 0
    total_time = 0.0
    for url_stat in get_url_stats(log_processed):
        stats.append(url_stat)
        total_count += url_stat['count']
        total_time += url_stat['time_sum']
    for i, _ in enumerate(stats):
        stats[i]['count_perc'] = stats[i]['count'] / total_count * 100
        stats[i]['time_perc'] = stats[i]['time_sum'] / total_time * 100
    
    stats.sort(key=lambda k: k['time_sum'], reverse=True)

    if limit:
        return stats[:limit]
    return stats


def get_url_stats(log_processed):
    for url in log_processed:
        requests_times = log_processed[url]
        url_stat = {
            'url': url,
            'count': len(requests_times),
            'count_perc': None,
            'time_sum': sum(requests_times),
            'time_perc': None,
            'time_avg': mean(requests_times),
            'time_max': max(requests_times),
            'time_med': median(requests_times)
        }
        yield url_stat
