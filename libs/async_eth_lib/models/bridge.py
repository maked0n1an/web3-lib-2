from typing import (
    Optional,
    Tuple
)

from . import exceptions as exceptions
from .contract import RawContract


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
        

# region Network DTO
class NetworkData:
    def __init__(
        self,
        chain_id: int,
        bridge_dict: dict[str, TokenBridgeInfo],
    ) -> None:
        self.chain_id = chain_id
        self.bridge_dict = bridge_dict
        

class FetcherBase:
    NETWORKS_DATA: dict[str, NetworkData] = {}
    
    @classmethod
    def get_network_data(
        cls,
        network_name: str
    ) -> NetworkData:
        if network_name not in cls.NETWORKS_DATA:
            raise exceptions.NetworkNotAdded(
                f"The '{network_name}' network has not been "
                f"added to {cls.__name__} networks dict"
            )

        network_data = cls.NETWORKS_DATA[network_name]

        return network_data
    
    @classmethod
    def get_chain_id(
        cls,
        network_name: str
    ) -> int | None:
        network_data = cls.get_network_data(network_name=network_name)

        return network_data.chain_id

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

class NetworkDataFetcher(FetcherBase):
    @classmethod
    def get_token_bridge_info(
        cls,
        network_name: str,
        token_symbol: str
    ) -> TokenBridgeInfo:
        token_symbol = token_symbol.upper()

        network_data = cls.get_network_data(network_name=network_name)

        cls._check_for_bridge_contract(
            cls=cls, token=token_symbol, bridge_dict=network_data.bridge_dict
        )

        token_bridge_info = network_data.bridge_dict[token_symbol]
        return token_bridge_info    
    
    @classmethod
    def get_pool_id(
        cls,
        network_name: str,
        token_symbol: str
    ) -> int | None:
        token_bridge_info = cls.get_token_bridge_info(
            network_name=network_name, token_symbol=token_symbol
        )

        return token_bridge_info.pool_id
    
    @classmethod
    def get_chain_id_and_pool_id(
        cls,
        network_name: str,
        token_symbol: str
    ) -> Tuple[int, Optional[int]]:
        token_symbol = token_symbol.upper()

        network_data = cls.get_network_data(network_name=network_name)

        cls._check_for_bridge_contract(
            cls=cls, token=token_symbol, bridge_dict=network_data.bridge_dict
        )

        chain_id = network_data.chain_id
        pool_id = network_data.bridge_dict[token_symbol].pool_id

        return (chain_id, pool_id)
    
            
class BridgeContractDataFetcher(FetcherBase): 
    @classmethod
    def get_only_contract_for_bridge(
        cls,
        network_name: str,
        token_symbol: str
    ) -> RawContract:
        token_symbol = token_symbol.upper()
        network_data = cls.get_network_data(network_name=network_name)
        
        cls._check_for_bridge_contract(
            cls=cls, token=token_symbol, bridge_dict=network_data.bridge_dict
        )
        
        bridge_raw_contract = network_data.bridge_dict[token_symbol]        
        
        return bridge_raw_contract
# endregion Network DTO