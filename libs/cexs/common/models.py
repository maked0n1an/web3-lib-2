import random
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


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

    def completely_filled(self) -> bool:
        return all((self.api_key, self.api_secret))

@dataclass
class OkxCredentials(CexCredentials):
    api_passphrase: str = None
    is_okx_eu_type: bool = False

    def completely_filled(self) -> bool:
        return all((self.api_key, self.api_secret, self.api_passphrase))


class Cex(ABC):
    def __init__(
        self,
        credentials: CexCredentials
    ):
        self.credentials = credentials

    @abstractmethod
    async def withdraw(
        self,
        ccy: str,
        amount: float,
        network_name: str,
        receiver_address: str,
        receiver_account_id: str = '',
        is_fee_included_in_request: bool = False
    ):
        """
        Initiates a withdrawal process for the specified cryptocurrency.

        Args:
            ccy (str): The currency code (e.g., 'ETH', 'BTC') for the withdrawal.
            amount (float): The amount of cryptocurrency to withdraw.
            network_name (str): The name of the blockchain network (e.g., 'Optimism', 'Ethereum').
            receiver_address (str): The recipient's cryptocurrency address to which the funds will be sent.
            receiver_account_id (str, optional): The recipient's account ID if applicable. Defaults to an empty string.
            is_fee_included_in_request (bool, optional): 
                If True, the soft will withdraw amount smaller than was requested because of fee.
                If False, the soft will withdraw the requested amount.
                Defaults to False.

        Returns:
            bool: True if the withdrawal is successful, False otherwise.
        """
        pass

    @abstractmethod
    async def wait_deposit_confirmation(
        self,
        ccy: str,
        amount: float,
        network_name: str,
        old_sub_balances: dict,
        check_time: int = 45
    ) -> bool:
        """
        Waits for the deposit confirmation of a specified cryptocurrency.

        Args:
            ccy (str): The currency code (e.g., 'ETH', 'BTC') for the deposit.
            amount (float): The amount of cryptocurrency deposited.
            network_name (str): The name of the blockchain network (e.g., 'Optimism', 'Ethereum').
            old_sub_balances (dict): A dictionary containing the old sub-balances before the deposit.
            check_time (int, optional): The time interval (in seconds) between checks for deposit confirmation. Defaults to 45 seconds.

        Returns:
            bool: True if the deposit is confirmed and reflected in the balances, False otherwise.
        """
        pass

    @abstractmethod
    async def get_min_dep_details(
        self,
        ccy: str = 'ETH'
    ) -> Optional[dict]:
        """
        Retrieve the minimum deposit details for a given cryptocurrency.

        Args:
            ccy (str): The cryptocurrency symbol to retrieve deposit details for.
                       Defaults to 'ETH'.

        Returns:
            Optional[dict]: A dictionary containing deposit details for each supported network,
                            or an empty dictionary if the token symbol is invalid. The details 
                            include deposit enablement status, minimum deposit amount, 
                            minimum confirmations, and minimum unlock confirmations.
        """
        pass

    @abstractmethod
    async def get_min_dep_details_for_network(
        self,
        ccy: str,
        network_name: str,
    ) -> dict:
        """
        Retrieve the minimum deposit details for a specific cryptocurrency and network.

        Args:
            ccy (str): The cryptocurrency symbol to retrieve deposit details for.
            network_name (str): The name of the network for which to retrieve deposit details.

        Returns:
            dict: A dictionary containing the deposit details for the specified cryptocurrency 
                  and network, or an empty dictionary if the network is unavailable or deposits 
                  are disabled. The details include deposit enablement status, minimum deposit 
                  amount, and required confirmations.
        """
        pass

    async def sleep(self, secs: float | tuple[float] = 1):
        if isinstance(secs, tuple):
            secs = random.choice(secs)
        await asyncio.sleep(secs)
