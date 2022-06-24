import logging
import logging.handlers
import multiprocessing
from logging.handlers import RotatingFileHandler

from flask import g


def set_logger_config(name=''):
    logger = logging.getLogger(name)
    setattr(g, 'log', logger)


def get_log():
    _log = getattr(g, 'log', None)
    if not _log:
        set_logger_config()
        _log = getattr(g, 'log', None)
    return _log


def get_sql_log():
    _log = getattr(g, 'sql_log', None)
    if not _log:
        _log = logging.getLogger('sql_log')
        setattr(g, 'sql_log', _log)

    return _log


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        _request_id = getattr(g, 'request_id', None)
        if _request_id:
            record.request_id = _request_id
            record.browser_uuid = g.browser_uuid
            record.ac_token_time = g.ac_token_time
        else:
            record.request_id = ""
            record.browser_uuid = ""
            record.ac_token_time = ""
        return True


class SafeRotatingFileHandler(RotatingFileHandler):
    """
    多进程下 RotatingFileHandler 会出现问题
    """

    _rollover_lock = multiprocessing.Lock()

    def emit(self, record):
        """
        Emit a record.

        Output the record to the file, catering for rollover as described
        in doRollover().
        """
        try:
            if self.shouldRollover(record):
                with self._rollover_lock:
                    if self.shouldRollover(record):
                        self.doRollover()
            logging.FileHandler.emit(self, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def shouldRollover(self, record):
        if self._should_rollover():
            # if some other process already did the rollover we might
            # checked log.1, so we reopen the stream and check again on
            # the right log file
            if self.stream:
                self.stream.close()
                self.stream = self._open()

            return self._should_rollover()

        return 0

    def _should_rollover(self):
        if self.maxBytes > 0:
            self.stream.seek(0, 2)
            if self.stream.tell() >= self.maxBytes:
                return True

        return False


def init_logging_config(app):
    base_config = app.config.copy()
    log_level = base_config.get('LOG_LEVEL', logging.INFO)
    log_path = base_config.get('LOG_PATH', '')

    logger = logging.getLogger('lint_code_saas')
    logger.setLevel(log_level)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] :[%(filename)s]:[%(funcName)s]:[%(request_id)s]:[%(browser_uuid)s]:[%(ac_token_time)s] %(message)s'
    )
    logger.addFilter(RequestIdFilter())
    if log_path:
        log_file = log_path + "view.log"
        rotate_handler = SafeRotatingFileHandler(log_file, "a", 100 * 1024 * 1024, 60)
        rotate_handler.setFormatter(formatter)
        logger.addHandler(rotate_handler)
    else:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    sql_logger = logging.getLogger('sql_log')
    sql_logger.setLevel(log_level)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] :[%(filename)s]:[%(funcName)s]:[%(request_id)s]:[%(browser_uuid)s]:[%(ac_token_time)s] %(message)s'
    )
    sql_logger.addFilter(RequestIdFilter())
    if log_path:
        log_file = log_path + "sql.log"
        rotate_handler = SafeRotatingFileHandler(log_file, "a", 100 * 1024 * 1024, 60)
        rotate_handler.setFormatter(formatter)
        sql_logger.addHandler(rotate_handler)
    else:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        sql_logger.addHandler(ch)

    cel_logger = logging.getLogger('lint_code_saas_celery')
    cel_logger.setLevel(log_level)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] :[%(filename)s]:[%(funcName)s] %(message)s')
    if log_path:
        log_file = log_path + "task.log"
        rotate_handler = SafeRotatingFileHandler(log_file, "a", 100 * 1024 * 1024, 60)
        rotate_handler.setFormatter(formatter)
        cel_logger.addHandler(rotate_handler)
    else:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        cel_logger.addHandler(ch)
