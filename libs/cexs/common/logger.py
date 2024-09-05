import os
import sys
import logging
from pathlib import Path

from libs.cexs.common.models import LogStatus


class CustomLogger:
    FOLDER_NAME: str = 'user_data/logs'
    LOGGERS: dict[str, logging.Logger] = {}
    
    def __init__(self):
        self._create_log_folder()
            
    @classmethod
    def _create_log_folder(cls):
        relative_path = Path(cls.FOLDER_NAME)
        relative_path.mkdir(parents=True, exist_ok=True)

    def _initialize_main_log(self) -> logging.Logger:
        if 'main_logger' not in self.LOGGERS:
            name_of_file = "main"

            main_logger = logging.getLogger(name_of_file)
            main_logger.setLevel(logging.DEBUG)

            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(MainConsoleLogFormatter())
            main_logger.addHandler(console_handler)

            file_handler = logging.FileHandler(f"{name_of_file}.log")
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(MainFileLogFormatter())
            main_logger.addHandler(file_handler)

            logging.addLevelName(200, LogStatus.SUCCESS)
            logging.addLevelName(201, LogStatus.FOUND)
            logging.addLevelName(202, LogStatus.SENT)
            logging.addLevelName(203, LogStatus.WITHDRAWN)
            logging.addLevelName(204, LogStatus.INFO)
            logging.addLevelName(210, LogStatus.DEPOSITED)
            
            logging.addLevelName(301, LogStatus.WARNING)
            
            logging.addLevelName(402, LogStatus.ERROR)
            logging.addLevelName(403, LogStatus.FAILED)

            self.LOGGERS["main_logger"] = main_logger

        return self.LOGGERS["main_logger"]
    
    def log_message(
        self, 
        account_id: str | int = '',
        address: str = '',
        network_name: str = '',
        status: str = '',
        message: str = '',
    ) -> None:
        message_with_calling_line = f"{self.__class__.__name__:<10} | {message}"
        
        main_logger = self._initialize_main_log()
        main_logger.log(
            level=logging.getLevelName(status),
            msg=message_with_calling_line,
            extra = {
                "account_id": account_id,
                "masked_address": (
                    address[:6] + "..." + address[-4:]
                    if address else address
                ),
                "network_name": (
                    network_name
                    if network_name else network_name
                )
            }
        )

class CustomLogData(logging.Formatter):
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    LOG_TIME_FORMAT = '%(asctime)s |'
    LOG_LEVELNAME_FORMAT = ' %(levelname)-9s '

    RED = "\x1b[31;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    BLUE = "\x1b[34;20m"
    WHITE = "\x1b[37;20m"
    GREY = "\x1b[38;20m"
    RESET = "\x1b[0m"

    SUCCESS_FORMAT = GREEN + LOG_LEVELNAME_FORMAT + RESET

    FORMATS = {
        LogStatus.INFO: WHITE + LOG_LEVELNAME_FORMAT + RESET,
        LogStatus.WARNING: YELLOW + LOG_LEVELNAME_FORMAT + RESET,
        LogStatus.SUCCESS: SUCCESS_FORMAT,
        LogStatus.ERROR: RED + LOG_LEVELNAME_FORMAT + RESET,
        LogStatus.FAILED: RED + LOG_LEVELNAME_FORMAT + RESET,

        LogStatus.DEPOSITED: SUCCESS_FORMAT,
        LogStatus.FOUND: SUCCESS_FORMAT,
        LogStatus.SENT: SUCCESS_FORMAT,
        LogStatus.WITHDRAWN: SUCCESS_FORMAT
    }

    def __init__(self, *args, **kwargs):
        self.root_folder = os.getcwd()
        super().__init__(*args, **kwargs)


class SettingsLogFormatter(CustomLogData):
    def __init__(
        self,
        log_levelname_format: str | dict
    ) -> logging.Formatter:
        super().__init__()
        self.log_levelname_format = log_levelname_format

    def format(self, record):
        format_parts = ['']
        
        if record.__dict__.get('account_id'):
            format_parts.append('%(account_id)8s ')
        if record.__dict__.get('masked_address'):
            if not record.__dict__.get('account_id'):
                format_parts.append('%(account_id)8s ')
            format_parts.append('%(masked_address)s ')
        if record.__dict__.get('network_name'):
            format_parts.append('%(network_name)-12s ')
        format_parts.append('%(message)s')
        
        log_message_format = '| '.join(format_parts)
        levelname = record.levelname
        
        if isinstance(self.log_levelname_format, dict):
            log_levelname_format = self.log_levelname_format[levelname]
        else:
            log_levelname_format = self.log_levelname_format

        if levelname in self.FORMATS:
            formatted_message = self.LOG_TIME_FORMAT + \
                log_levelname_format + log_message_format
            formatter = logging.Formatter(
                formatted_message,
                datefmt=self.TIME_FORMAT
            )

        return formatter.format(record)

class MainConsoleLogFormatter(SettingsLogFormatter):
    def __init__(self):
        super().__init__(
            self.FORMATS,
        )

    def format(self, record):
        return super().format(record)


class MainFileLogFormatter(SettingsLogFormatter):
    def __init__(self):
        super().__init__(
            self.LOG_LEVELNAME_FORMAT,
        )

    def format(self, record):
        return super().format(record)