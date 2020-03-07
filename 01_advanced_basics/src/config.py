import json
import logging


def prepare_config(config_base, config_path, log_formatter=None):
    updated_conf = config_base.copy()
    if config_path:
        try:
            with open(config_path, 'r', encoding='utf-8') as conf:
                config_from_file = json.load(conf)
        except OSError:
            logging.error(f"Config file not found: {config_path}")
            return
        except json.decoder.JSONDecodeError:
            logging.error(f"Failed parse config: {config_path}")
            return
        except BaseException:
            logging.exception("Unknown exception with config")
            return
        updated_conf.update(config_from_file)

        if log_formatter and "LOGGER_FILE" in updated_conf:
            try:
                root_logger = logging.getLogger()
                file_handler = logging.FileHandler(updated_conf['LOGGER_FILE'])
                file_handler.setFormatter(log_formatter)
                root_logger.addHandler(file_handler)
            except OSError:
                msg = "Logger_file not found in config: {}"
                logging.error(msg.format(updated_conf['LOGGER_FILE']))
                return

    return updated_conf
