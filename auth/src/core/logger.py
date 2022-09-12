# from typing import Any
#
#
# ERROR_LOG_FILENAME = ".auth-errors.log"
# DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# DEFAULT_LOG_HANDLERS = [
#     "verbose_output",
# ]
# LOGGING: dict[str, Any] = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "default": {
#             "format": DEFAULT_LOG_FORMAT,
#         },
#         "json": {
#             "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
#             "format": """
#             asctime: %(asctime)s
#             created: %(created)f
#             filename: %(filename)s
#             funcName: %(funcName)s
#             levelname: %(levelname)s
#             levelno: %(levelno)s
#             lineno: %(lineno)d
#             message: %(message)s
#             module: %(module)s
#             msec: %(msecs)d
#             name: %(name)s
#             pathname: %(pathname)s
#             process: %(process)d
#             processName: %(processName)s
#             relativeCreated: %(relativeCreated)d
#             thread: %(thread)d
#             threadName: %(threadName)s
#             exc_info: %(exc_info)s
#             request_id: %(request_id)s
#         """,
#         },
#     },
#     "handlers": {
#         "logfile": {
#             "level": "INFO",
#             "class": "logging.handlers.RotatingFileHandler",
#             "filename": ERROR_LOG_FILENAME,
#             "backupCount": 2,
#             "formatter": "default",
#         },
#         "verbose_output": {
#             "level": "INFO",
#             "class": "logging.StreamHandler",
#             "formatter": "default"
#         },
#         "json": {
#             "level": "INFO",
#             "class": "logging.handlers.RotatingFileHandler",
#             "filename": ERROR_LOG_FILENAME,
#             "backupCount": 2,
#             "formatter": "json",
#         },
#     },
#     "loggers": {
#         "werkzeug": {
#             "level": "INFO",
#             "handlers": [
#                 "json",
#             ],
#         }
#     },
#     "root": {
#         "level": "WARNING",
#         "formatter": "verbose",
#         "handlers": DEFAULT_LOG_HANDLERS,
#     },
# }
