import inspect
import logging
import os
import sys
from pathlib import Path

from ..models.others import LogStatus


class CustomLogger:
    FOLDER_NAME: str = 'user_data/logs'
    LOGGERS: dict[str, logging.Logger] = {}

    def __init__(
        self,
        account_id: str | int,
        address: str,
        create_log_file_per_account: bool = False
    ) -> None:
        self.account_id = account_id
        self.masked_address = (
            f"{hex(address)[:6]}...{hex(address)[-4:]}"
            if address else ''
        )
        self.network_name = 'Starknet'
        self.create_log_file_per_account = create_log_file_per_account
        if create_log_file_per_account:
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
            console_handler.setFormatter(ConsoleLogFormatter())
            main_logger.addHandler(console_handler)

            file_handler = logging.FileHandler(f"{name_of_file}.log")
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(FileLogFormatter())
            main_logger.addHandler(file_handler)

            logging.addLevelName(403, LogStatus.FAILED)
            logging.addLevelName(204, LogStatus.SUCCESS)

            logging.addLevelName(210, LogStatus.APPROVED)
            logging.addLevelName(201, LogStatus.MINTED)
            logging.addLevelName(202, LogStatus.BRIDGED)
            logging.addLevelName(203, LogStatus.SWAPPED)
            logging.addLevelName(205, LogStatus.DEPOSITED)
            logging.addLevelName(206, LogStatus.WITHDRAWN)

            self.LOGGERS["main_logger"] = main_logger

        return self.LOGGERS["main_logger"]

    def _initialize_account_log(self, account_id: str) -> logging.Logger:
        if account_id not in self.LOGGERS:
            name_of_file = f'{self.FOLDER_NAME}/log_{account_id}'
            
            wallet_logger = logging.getLogger(name_of_file)
            file_handler = logging.FileHandler(f"{name_of_file}.log")
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(FileLogFormatter())
            wallet_logger.addHandler(file_handler)

            self.LOGGERS[account_id] = wallet_logger

        return self.LOGGERS[account_id]

    def log_message(
        self, 
        status: str, 
        message: str, 
    ) -> None:
        caller_frame = inspect.currentframe().f_back
        full_file_name = os.path.basename(caller_frame.f_code.co_filename)
        file_name = os.path.splitext(full_file_name)[0].capitalize()
        message_with_calling_line = f"{file_name:<10} | {message}"
        
        extra = {
            "account_id": self.account_id,
            "masked_address": self.masked_address,
            "network_name": self.network_name
        }

        main_logger = self._initialize_main_log()
        main_logger.log(
            level=logging.getLevelName(status),
            msg=message_with_calling_line,
            extra=extra
        )

        if self.create_log_file_per_account:
            logger = self._initialize_account_log(self.account_id)
            logger.log(
                level=logging.getLevelName(status),
                msg=message_with_calling_line,
                extra=extra
            )


class CustomLogData(logging.Formatter):
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    LOG_TIME_FORMAT = '%(asctime)s |'
    LOG_LEVELNAME_FORMAT = ' %(levelname)-10s '

    RED = "\x1b[31;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    BLUE = "\x1b[34;20m"
    WHITE = "\x1b[37;20m"
    GREY = "\x1b[38;20m"
    RESET = "\x1b[0m"

    SUCCESS_FORMAT = GREEN + LOG_LEVELNAME_FORMAT + RESET

    FORMATS = {
        LogStatus.DEBUG: BLUE + LOG_LEVELNAME_FORMAT + RESET,
        LogStatus.INFO: WHITE + LOG_LEVELNAME_FORMAT + RESET,
        LogStatus.WARNING: YELLOW + LOG_LEVELNAME_FORMAT + RESET,
        LogStatus.SUCCESS: SUCCESS_FORMAT,
        LogStatus.ERROR: RED + LOG_LEVELNAME_FORMAT + RESET,
        LogStatus.FAILED: RED + LOG_LEVELNAME_FORMAT + RESET,

        LogStatus.APPROVED: SUCCESS_FORMAT,
        LogStatus.MINTED: SUCCESS_FORMAT,
        LogStatus.BRIDGED: SUCCESS_FORMAT,
        LogStatus.SWAPPED: SUCCESS_FORMAT,
        LogStatus.DEPOSITED: SUCCESS_FORMAT,
        LogStatus.WITHDRAWN: SUCCESS_FORMAT,
    }

    def __init__(self, *args, **kwargs):
        self.root_folder = os.getcwd()
        super().__init__(*args, **kwargs)


class SettingsLogFormatter(CustomLogData):
    def __init__(
        self,
        log_levelname_format: str | dict,
    ) -> logging.Formatter:
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


class ConsoleLogFormatter(SettingsLogFormatter):
    def __init__(self):
        super().__init__(self.FORMATS)

    def format(self, record):
        return super().format(record)


class FileLogFormatter(SettingsLogFormatter):
    def __init__(self):
        super().__init__(self.LOG_LEVELNAME_FORMAT)

    def format(self, record):
        return super().format(record)


class ConsoleLoggerSingleton:
    _instance = None

    @staticmethod
    def get_logger():
        if ConsoleLoggerSingleton._instance is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(ConsoleLogFormatter())
            logger.addHandler(console_handler)

            console_handler = logging.FileHandler("main.log")
            console_handler.setFormatter(FileLogFormatter())
            logger.addHandler(console_handler)
            ConsoleLoggerSingleton._instance = logger

        return ConsoleLoggerSingleton._instance


console_logger = ConsoleLoggerSingleton.get_logger()