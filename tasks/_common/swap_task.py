from web3.types import TxParams

from libs.async_eth_lib.architecture.client import Client
from libs.async_eth_lib.data.token_contracts import ContractsFactory
from libs.async_eth_lib.models.others import ParamsTypes, TokenAmount
from libs.async_eth_lib.models.swap import SwapInfo, SwapProposal
from tasks._common.utils import Utils, PriceUtils


class SwapTask(Utils, PriceUtils):
    def __init__(self, client: Client):
        self.client = client
        
    def validate_swap_inputs(
        self,
        first_arg: str,
        second_arg: str,
        param_type: str = 'args',
        function: str = 'swap'
    ) -> str:
        """
        Validate inputs for a swap operation.

        Args:
            first_arg (str): The first argument.
            second_arg (str): The second argument.
            param_type (str): The type of arguments (default is 'args').
            message (str): The message (default is 'swap')

        Returns:
            str: A message indicating the result of the validation.
        """
        if first_arg.upper() == second_arg.upper():
            return f'The {param_type} for {function}() are equal: {first_arg} == {second_arg}'

    def set_all_gas_params(
        self,
        swap_info: SwapInfo,
        tx_params: dict | TxParams
    ) -> dict | TxParams:
        """
        Set gas-related parameters in the transaction parameters based on provided SwapInfo.

        Iterates over gas-related attributes in SwapInfo and invokes corresponding methods on
        self.client.contract to modify tx_params accordingly.

        Args:
            swap_info (SwapInfo): Information about the swap containing gas-related attributes.
            tx_params (dict or TxParams): Transaction parameters to be modified.

        Returns:
            dict or TxParams: Updated transaction parameters after gas-related modifications.
        """
        method_mappings = {
            'gas_limit': 'set_gas_limit',
            'gas_price': 'set_gas_price',
            'multiplier_of_gas': 'add_multiplier_of_gas'
        }
        
        for attr, method_name in method_mappings.items():
            if getattr(swap_info, attr):
                tx_params = getattr(self.client.contract, method_name)(
                    getattr(swap_info, attr),
                    tx_params=tx_params
                )

        return tx_params
    
    async def approve_interface(
        self,
        swap_info: SwapInfo,
        token_contract: ParamsTypes.TokenContract,
        spender_address: ParamsTypes.Address,
        amount: ParamsTypes.Amount | None = None,
        tx_params: TxParams | dict | None = None,
        is_approve_infinity: bool = None
    ) -> str | bool:
        """
        Approve spending of a specific amount by a spender on behalf of the owner.

        Args:
            token_contract (ParamsTypes.TokenContract): The token contract instance.
            spender_address (ParamsTypes.Address): The address of the spender.
            amount (TokenAmount | None): The amount to approve (default is None).
            gas_price (float | None): Gas price for the transaction (default is None).
            gas_limit (int | None): Gas limit for the transaction (default is None).
            is_approve_infinity (bool): Whether to approve an infinite amount (default is True).

        Returns:
            bool: True if the approval is successful, False otherwise.
        """
        balance = await self.client.contract.get_balance(
            token_contract=token_contract
        )
        if balance.Wei <= 0:
            return True

        if not amount or amount.Wei > balance.Wei:
            amount = balance

        approved = await self.client.contract.get_approved_amount(
            token_contract=token_contract,
            spender_address=spender_address,
            owner=self.client.account_manager.account.address
        )

        if amount.Wei <= approved.Wei:
            return True
        
        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        tx = await self.client.contract.approve(
            token_contract=token_contract,
            spender_address=spender_address,
            amount=amount,
            tx_params=tx_params,
            is_approve_infinity=is_approve_infinity
        )

        return tx
    
    async def compute_source_token_amount(
        self,
        swap_info: SwapInfo
    ) -> SwapProposal:
        """
        Compute the source token amount for a given swap.

        Args:
            swap_info (SwapInfo): Information about the swap.

        Returns:
            TokenSwapProposal: The prepared proposal for the swap.
        """
        from_token = ContractsFactory.get_contract(
            network_name=self.client.account_manager.network.name,
            token_symbol=swap_info.from_token
        )

        if from_token.is_native_token:
            balance = await self.client.contract.get_balance()
            decimals = balance.decimals

        else:
            balance = await self.client.contract.get_balance(from_token)
            decimals = balance.decimals

        if not swap_info.amount:
            token_amount = balance

        elif swap_info.amount:
            token_amount = TokenAmount(
                amount=swap_info.amount,
                decimals=decimals
            )
            if token_amount.Wei > balance.Wei:
                token_amount = balance

        elif swap_info.amount_by_percent:
            token_amount = TokenAmount(
                amount=balance.Wei * swap_info.amount_by_percent,
                decimals=decimals,
                wei=True
            )
        
        return SwapProposal(
            from_token=from_token,
            amount_from=token_amount
        )
        
    async def compute_min_destination_amount(
        self,
        swap_request: SwapProposal,
        min_to_amount: int,
        swap_info: SwapInfo,
        is_to_token_price_wei: bool = False
    ) -> SwapProposal:
        """
        Compute the minimum destination amount for a given swap.

        Args:
            swap_request (SwapRequest): The query for the swap.
            to_token_price (float): The price of the destination token.
            slippage (int): The slippage tolerance.

        Returns:
            TokenSwapProposal: The updated proposal with the minimum destination amount.
        """

        if not swap_request.to_token:
            swap_request.to_token = ContractsFactory.get_contract(
                network_name=self.client.account_manager.network.name,
                token_symbol=swap_info.to_token
            )

        decimals = await self.client.contract.get_decimals(
            token_contract=swap_request.to_token
        )

        min_amount_out = TokenAmount(
            amount=min_to_amount * (1 - swap_info.slippage / 100),
            decimals=decimals,
            wei=is_to_token_price_wei
        )

        return SwapProposal(
            from_token=swap_request.from_token,
            amount_from=swap_request.amount_from,
            to_token=swap_request.to_token,
            min_to_amount=min_amount_out
        )