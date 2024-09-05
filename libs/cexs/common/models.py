import random
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass


class LogStatus:
    FOUND = 'FOUND'
    SENT = 'SENT'
    DEPOSITED = 'DEPOSITED'
    WITHDRAWN = 'WITHDRAWN'

    WARNING = 'WARNING'
    SUCCESS = 'SUCCESS'
    INFO = 'INFO'
    ERROR = 'ERROR'
    FAILED = 'FAILED'


@dataclass
class CexCredentials:
    api_key: str
    api_secret: str
    api_passphrase: str = None

    def completely_filled(self) -> bool:
        return all((self.api_key, self.api_secret))

    def is_added_passphrase(self) -> bool:
        return bool(self.api_passphrase)


class OkxCredentials(CexCredentials):
    is_okx_eu_type: bool = False


class Cex(ABC):
    def __init__(
        self,
        credentials: CexCredentials
    ):
        self.credentials = credentials

    @abstractmethod
    async def withdraw(self):
        pass

    @abstractmethod
    async def wait_deposit_confirmation(self):
        pass

    async def sleep(self, secs: float | tuple[float] = 1):
        if isinstance(secs, tuple):
            secs = random.choice(secs)
        await asyncio.sleep(secs)
