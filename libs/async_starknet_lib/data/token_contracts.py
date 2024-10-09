from ..models.contract import (
    NativeTokenContract, 
    TokenContract
)
from ..models.others import TokenSymbol
from ..models.exceptions import ContractNotExists
from ..models.common import Singleton


class TokenContractData(metaclass=Singleton):
    ZERO_ADDRESS = ''

    @classmethod
    def get_token(
        cls,
        token_symbol: str, 
        project_prefix: str | None = None,
    ) -> TokenContract:
        contract_name = (
            f'{token_symbol.upper()}_{project_prefix.upper()}'
            if project_prefix
            else f'{token_symbol.upper()}'
        )

        if not hasattr(cls, contract_name):
            raise ContractNotExists(
                f"The contract has not been added "
                f"to {__class__.__name__} contracts"
            )

        return getattr(cls, contract_name)
    
    
# region All token contracts
class StarknetTokenContracts(TokenContractData):
    ETH = NativeTokenContract(title=TokenSymbol.ETH)
    
    USDT = TokenContract(
        title=TokenSymbol.USDT,
        address=0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8,
    )

    USDC = TokenContract(
        title=TokenSymbol.USDC,
        address=0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8,
        decimals=6
    )

    DAI = TokenContract(
        title=TokenSymbol.DAI,
        address=0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3,
        decimals=18
    )
    
    WBTC = TokenContract(
        title=TokenSymbol.WBTC,
        address=0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac,
        decimals=8
    )
        
    STRK = TokenContract(
        title=TokenSymbol.STRK,
        address=0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d,
        decimals=18
    )
# endregion All token contracts