import asyncio
import inspect
import aiohttp
from web3.types import TxParams

from libs.async_eth_lib.architecture.client import Client
from libs.async_eth_lib.data.token_contracts import ContractsFactory
from libs.async_eth_lib.models.others import LogStatus, ParamsTypes, TokenAmount, TokenSymbol
from libs.async_eth_lib.models.swap import SwapInfo, SwapProposal


# region To construct tx
class Utils:
    async def get_token_info(client: Client, token_address):
        """
        Fetches and prints information about a token from the blockchain.

        Args:
            client (Client): The blockchain client used to interact with the network.
            token_address (str): The address of the token contract on the blockchain.

        Returns:
            None
        """
        contract = await client.contract.get_token_contract(token=token_address)
        print('name:', await contract.functions.name().call())
        print('symbol:', await contract.functions.symbol().call())
        print('decimals:', await contract.functions.decimals().call())

    def to_cut_hex_prefix_and_zfill(self, data: str, length: int = 64):
        """
        Convert the string to lowercase and fill it with zeros to the specified length.

        Args:
            length (int): The desired length of the string after filling.

        Returns:
            str: The modified string.
        """
        return data[2:].zfill(length)

    @staticmethod
    def parse_params(
        params: str,
        has_function_signature: bool = True
    ) -> None:
        """
        Parse a string of parameters, optionally printing function signature and memory addresses.

        Args:
            params (str): The string of parameters to parse.
            has_function_signature (bool, optional): Whether to print the function signature (default is True).

        Returns:
            None
        """
        if has_function_signature:
            function_signature = params[:10]
            print('Function signature:', function_signature)
            params = params[10:]

        count = 0
        while params:
            memory_address = hex(count * 32)[2:].zfill(3)
            print(f'{memory_address}: {params[:64]}')
            count += 1
            params = params[64:]
# endregion To construct tx


# region To get prices
class PriceUtils:
    STABLES = {
        TokenSymbol.USDT:   1.0,
        TokenSymbol.USDC:   1.0,
        TokenSymbol.USDC_E: 1.0,
        TokenSymbol.USDV:   1.0
    }

    async def get_binance_ticker_price(
        self,
        first_token: str = TokenSymbol.ETH,
        second_token: str = TokenSymbol.USDT
    ) -> float | None:
        first_token = first_token.lstrip('W')
        second_token = second_token.lstrip('W')

        if first_token in self.STABLES and second_token in self.STABLES:
            return 1.0

        async with aiohttp.ClientSession() as session:
            price = await self._get_price_from_binance(session, first_token, second_token)
            if price:
                return price
            else:
                return await self._get_price_from_binance(session, second_token, first_token)

    async def _get_price_from_binance(
        self,
        session: aiohttp.ClientSession,
        first_token: str,
        second_token: str
    ) -> float | None:
        first_token, second_token = first_token.upper(), second_token.upper()
        for _ in range(5):
            try:
                response = await session.get(
                    f'https://api.binance.com/api/v3/ticker/price?symbol={first_token}{second_token}')
                if response.status != 200:
                    return None
                result_dict = await response.json()
                if 'price' in result_dict:
                    return float(result_dict['price'])
            except Exception as e:
                await asyncio.sleep(2)
        raise ValueError(
            f'Can not get {first_token}{second_token} price from Binance')
# endregion To get prices


# region Base class for actions
class BaseTask(Utils, PriceUtils):
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
        tx_params: TxParams | dict,
        amount: ParamsTypes.Amount | None = None,
        is_approve_infinity: bool = None
    ) -> str | bool:
        """
        Approve spending of a specific amount by a spender on behalf of the owner.

        Args:
            token_contract (ParamsTypes.TokenContract): The token contract instance.
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
            spender_address=tx_params['to'],
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
            tx_params=tx_params,
            amount=amount,
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
            token_symbol=swap_info.src_token_name
        )

        if from_token.is_native_token:
            balance = await self.client.contract.get_balance()
            decimals = balance.decimals

        else:
            balance = await self.client.contract.get_balance(from_token)
            decimals = balance.decimals

        if swap_info.amount:
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
        else:
            token_amount = balance

        return SwapProposal(
            from_token=from_token,
            amount_from=token_amount
        )

    async def compute_min_destination_amount(
        self,
        swap_proposal: SwapProposal,
        min_to_amount: int,
        swap_info: SwapInfo,
        is_to_token_price_wei: bool = False
    ) -> SwapProposal:
        """
        Compute the minimum destination amount for a swap proposal.

        Args:
            swap_proposal (SwapProposal): The initial swap proposal.
            min_to_amount (int): The minimum amount of the destination token.
            swap_info (SwapInfo): Information about the swap.
            is_to_token_price_wei (bool, optional): Whether the price of the destination token is in wei. Defaults to False.

        Returns:
            SwapProposal: The updated swap proposal with the minimum destination amount.
        """

        if not swap_proposal.to_token:
            swap_proposal.to_token = ContractsFactory.get_contract(
                network_name=self.client.account_manager.network.name,
                token_symbol=swap_info.dst_token_name
            )

        decimals = await self.client.contract.get_decimals(
            token_contract=swap_proposal.to_token
        )

        min_amount_out = TokenAmount(
            amount=float(min_to_amount) * (1 - swap_info.slippage / 100),
            decimals=decimals,
            wei=is_to_token_price_wei
        )

        return SwapProposal(
            from_token=swap_proposal.from_token,
            amount_from=swap_proposal.amount_from,
            to_token=swap_proposal.to_token,
            min_to_amount=min_amount_out
        )
# endregion Base class for actions
