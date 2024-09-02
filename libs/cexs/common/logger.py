import os
import sys
import inspect
import logging
from pathlib import Path
from typing import Optional, Union

from libs.cexs.common.models import LogStatus


class CustomLogger:
    FOLDER_NAME: str = 'user_data/logs'
    LOGGERS: dict[str, logging.Logger] = {}
    
    @property
    def account_id(self) -> str: 
        return self._account_id
    
    @account_id.setter
    def account_id(self, acc_id: str | int):
        self._account_id = acc_id
    
    @property
    def masked_address(self) -> str: 
        return self._masked_address
    
    @masked_address.setter
    def masked_address(self, address: Optional[str] = None):
        if not address:
            self._masked_address = address
        else:
            self._masked_address = address[:6] + "..." + address[-4:]
    
    @property
    def network_name(self) -> str:
        return self._network_name
    
    @network_name.setter
    def network_name(self, value: str):
        self._network_name = value
        
    def __init__(self):
        self.account_id = ''
        self.masked_address = ''
        self.network_name = ''
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
        status: str, 
        message: str,
        extra: dict
    ) -> None:
        class_name = self.__class__.__name__
        message_with_calling_line = f"{class_name:<12} | {message}"

        main_logger = self._initialize_main_log()
        main_logger.log(
            level=logging.getLevelName(status),
            msg=message_with_calling_line,
            extra=extra
        )

class CustomLogData(logging.Formatter):
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    LOG_TIME_FORMAT = '%(asctime)s |'
    LOG_LEVELNAME_FORMAT = ' %(levelname)-9s '
    # LOG_MESSAGE_FORMAT = '| %(id)8s | %(address)s | %(message)s' # | %(network)s

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
        
        if 'id' in record.__dict__:
            format_parts.append('%(id)8s ')
        if record.__dict__.get('address'):
            format_parts.append('%(address)s ')
        if record.__dict__.get('network'):
            format_parts.append('%(network)-12s ')
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
            # self.LOG_MESSAGE_FORMAT,
        )

    def format(self, record):
        return super().format(record)


class MainFileLogFormatter(SettingsLogFormatter):
    def __init__(self):
        super().__init__(
            self.LOG_LEVELNAME_FORMAT,
            # self.LOG_MESSAGE_FORMAT,
        )

    def format(self, record):
        return super().format(record)