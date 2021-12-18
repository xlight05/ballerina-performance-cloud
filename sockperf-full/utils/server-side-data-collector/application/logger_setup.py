import logging
import os
from datetime import datetime

# Logger formats
LOGGING_FORMAT = "%(asctime)s - %(filename)s - %(levelname)s: %(message)s"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Logger Setup
class OneLineExceptionFormatter(logging.Formatter):
    """ Format error traceback to single line. """

    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return repr(result)

    def format(self, record):
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        return result


class ContextFilter(logging.Filter):
    """ Add time stamp to the error log. """

    @staticmethod
    def time_format(timestamp):
        return datetime.fromtimestamp(timestamp).strftime(TIME_FORMAT)

    def filter(self, record):
        record.timestamp = self.time_format(record.created)
        return True


handler = logging.StreamHandler()
formatter = OneLineExceptionFormatter(LOGGING_FORMAT)
formatter.usesTime()
handler.setFormatter(formatter)
logger = logging.getLogger("application")
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))
logger.addHandler(handler)
context_filter = ContextFilter()
logger.addFilter(context_filter)
