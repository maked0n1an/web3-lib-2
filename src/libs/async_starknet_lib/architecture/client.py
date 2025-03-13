from starknet_py.net.account.account import Account
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import (
    StarkCurveSigner,
    KeyPair
)

from .contract import Contract
from .logger import CustomLogger
from .starknet_utils import StarknetNodeClient


class StarknetClient(StarknetNodeClient):
    CHAIN_ID = StarknetChainId.MAINNET

    def __init__(
        self,
        account_id: str | int,
        address: str,
        private_key: str,
        proxy: str | None = None,
        check_proxy: bool = False,
        create_log_file_per_account: bool = True
    ):
        self.address = address
        self.account_id = account_id
        self.proxy = proxy
        
        self.node_client = self.init_node_client(self.proxy, check_proxy)
        self.key_pair = KeyPair.from_private_key(private_key)
        self.signer = StarkCurveSigner(address, self.key_pair, self.CHAIN_ID)
        self.account = Account(
            address=self.address,
            client=self.node_client,
            key_pair=self.key_pair,
            chain=self.CHAIN_ID
        )
        self._init_logger(create_log_file_per_account)
        
        self.contract = Contract(self.account)
        self.network_decimals = 18

    async def __aexit__(self, exc_type, exc, tb):
        await super().__aexit__(exc_type, exc, tb)

    def _init_logger(
        self,
        create_log_file_per_account: bool
    ) -> None:
        self.custom_logger = CustomLogger(
            account_id=self.account_id,
            address=self.account.address,
            create_log_file_per_account=create_log_file_per_account
        )
