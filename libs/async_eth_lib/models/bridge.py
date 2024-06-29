from typing import (
    Optional,
    Tuple
)

import async_eth_lib.models.exceptions as exceptions
from async_eth_lib.models.contract import RawContract


# region About token bridge
class TokenBridgeInfo:
    def __init__(
        self,
        bridge_contract: RawContract,
        pool_id: int | None = None
    ) -> None:
        self.bridge_contract = bridge_contract
        self.pool_id = pool_id
# endregion About token bridge        
        

# region For network info while bridge
class NetworkData:
    def __init__(
        self,
        chain_id: int,
        bridge_dict: dict[str, TokenBridgeInfo],
    ) -> None:
        self.chain_id = chain_id
        self.bridge_dict = bridge_dict
        

class NetworkDataFetcher:
    networks_data: dict[str, NetworkData] = {}

    @classmethod
    def get_chain_id(
        cls,
        network: str
    ) -> int | None:
        network_data = cls.get_network_data(network=network)

        return network_data.chain_id

    @classmethod
    def get_pool_id(
        cls,
        network: str,
        token_symbol: str
    ) -> int | None:
        token_bridge_info = cls.get_token_bridge_info(
            network=network, token_symbol=token_symbol
        )

        return token_bridge_info.pool_id

    @classmethod
    def get_chain_id_and_pool_id(
        cls,
        network: str,
        token_symbol: str
    ) -> Tuple[int, Optional[int]]:
        token_symbol = token_symbol.upper()

        network_data = cls.get_network_data(network=network)

        cls._check_for_bridge_contract(
            cls=cls, token=token_symbol, bridge_dict=network_data.bridge_dict
        )

        chain_id = network_data.chain_id
        pool_id = network_data.bridge_dict[token_symbol].pool_id

        return (chain_id, pool_id)

    @classmethod
    def get_token_bridge_info(
        cls,
        network: str,
        token_symbol: str
    ) -> TokenBridgeInfo:
        token_symbol = token_symbol.upper()

        network_data = cls.get_network_data(network=network)

        cls._check_for_bridge_contract(
            cls=cls, token=token_symbol, bridge_dict=network_data.bridge_dict
        )

        token_bridge_info = network_data.bridge_dict[token_symbol]
        return token_bridge_info

    @classmethod
    def get_network_data(
        cls,
        network: str
    ) -> NetworkData:
        network = network.lower()
        networks_data = cls.networks_data

        if network not in networks_data:
            raise exceptions.NetworkNotAdded(
                f"The '{network.capitalize()}' network has not been "
                f"added to {cls.__name__} networks dict"
            )

        network_data = networks_data[network]

        return network_data

    def _check_for_bridge_contract(
        cls,
        token: str,
        bridge_dict: dict[str, TokenBridgeInfo]
    ) -> None:
        if token not in bridge_dict:
            raise exceptions.ContractNotExists(
                f"The bridge contract for {token} has not been added "
                f"to {cls.__name__} bridge contracts"
            )
# endregion For network info while bridge