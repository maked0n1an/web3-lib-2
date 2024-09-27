from ..models import exceptions
from ..models.others import TokenSymbol
from ..models.contract import NativeTokenAccount, TokenAccount


class TokenContractData:
    @classmethod
    def get_token(
        cls,
        token_symbol: str,  # GETH (GETH, LZ)
        project_prefix: str | None = None,  # LZ
    ) -> TokenAccount:
        contract_name = (
            f'{token_symbol.upper()}_{project_prefix.upper()}'
            if project_prefix
            else f'{token_symbol.upper()}'
        )

        if not hasattr(cls, contract_name):
            raise exceptions.ContractNotExists(
                f"The contract has not been added "
                f"to {__class__.__name__} contracts"
            )

        return getattr(cls, contract_name)


class AptosTokenAccounts(TokenContractData):
    APT = NativeTokenAccount(TokenSymbol.APT)
    
    USDT_LZ = TokenAccount(
        title=TokenSymbol.USDT,
        address='0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDT',
        decimals=6
    )
    USDC_LZ = TokenAccount(
        title=TokenSymbol.USDC,
        address='0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC',
        decimals=6
    )
    WETH_LZ = TokenAccount(
        title=TokenSymbol.WETH,
        address='0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::WETH',
        decimals=6
    )
    WBTC_LZ = TokenAccount(
        title=TokenSymbol.WBTC,
        address='0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::WBTC',
        decimals=6
    )
