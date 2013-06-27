import logging
import logging.handlers


def setup_logger(logger_name, toConsole, log_file, level=logging.INFO):
  l = logging.getLogger(logger_name)
  l.setLevel(level)

  if logger_name == "":
    logger_name = "MAIN"
  logFormat = logger_name.ljust(5) + ' | %(asctime)s | %(levelname)-7s | %(message)s'
  dateFormat = '%Y-%m-%d %H:%M:%S'
  formatter = logging.Formatter(logFormat, dateFormat)

  if log_file is not None:
    fileHandler = logging.handlers.RotatingFileHandler(log_file, maxBytes=500000, backupCount=10)
    fileHandler.setFormatter(formatter)
    l.addHandler(fileHandler)

  if toConsole:
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    l.addHandler(streamHandler)


setup_logger('', True, 'main.log')
setup_logger('test', False, 'test.log')


logging.info("to logging")
l = logging.getLogger('test')
l.info("to test")
