import asyncio
import aiohttp
from web3.types import TxParams

from libs.async_eth_lib.architecture.client import Client
from libs.async_eth_lib.data.token_contracts import ContractsFactory
from libs.async_eth_lib.models.contract import RawContract
from libs.async_eth_lib.models.others import ParamsTypes, TokenAmount, TokenSymbol
from libs.async_eth_lib.models.operation import OperationInfo, OperationProposal


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

    @staticmethod
    def to_cut_hex_prefix_and_zfill(hex_data: str, length: int = 64):
        """
        Convert the hex string to lowercase, remove the '0x' prefix, and fill it with zeros to the specified length.

        Args:
            hex_data (str): The original hex string.
            length (int): The desired length of the string after filling. The default is 64.

        Returns:
            str: The modified string with '0x' prefix removed and zero-filled to the specified length.
        """
        if hex_data.startswith('0x'):
            hex_data = hex_data[2:]
        else:
            raise ValueError("Hex address must start with '0x'")
        
        return hex_data.zfill(length)
    
    @staticmethod
    def normalize_non_evm_hex_value(hex_value: str, length: int = 64) -> str:
        hex_value = BaseTask.to_cut_hex_prefix_and_zfill(hex_value, length)
        return '0x' + hex_value

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
        operation_info: OperationInfo,
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
            if getattr(operation_info, attr):
                tx_params = getattr(self.client.contract, method_name)(
                    getattr(operation_info, attr),
                    tx_params=tx_params
                )

        return tx_params

    async def approve_interface(
        self,
        operation_info: OperationInfo,
        token_contract: RawContract,
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
            owner=self.client.account.address
        )

        if amount.Wei <= approved.Wei:
            return True

        tx_params = self.set_all_gas_params(
            operation_info=operation_info,
            tx_params=tx_params
        )

        optional_tx_hash = await self.client.contract.approve(
            token_contract=token_contract,
            tx_params=tx_params,
            amount=amount,
            is_approve_infinity=is_approve_infinity
        )

        return optional_tx_hash

    async def compute_source_token_amount(
        self,
        operation_info: OperationInfo
    ) -> OperationProposal:
        """
        Compute the source token amount for a given swap.

        Args:
            swap_info (SwapInfo): Information about the swap.

        Returns:
            TokenSwapProposal: The prepared proposal for the swap.
        """
        from_token = ContractsFactory.get_contract(
            network_name=self.client.network.name,
            token_symbol=operation_info.from_token_name
        )

        if from_token.is_native_token:
            balance = await self.client.contract.get_balance()
            decimals = balance.decimals

        else:
            balance = await self.client.contract.get_balance(from_token)
            decimals = balance.decimals

        if operation_info.amount:
            amount_from = TokenAmount(
                amount=operation_info.amount,
                decimals=decimals
            )
            if amount_from.Wei > balance.Wei:
                amount_from = balance

        elif operation_info.amount_by_percent:
            amount_from = TokenAmount(
                amount=balance.Wei * operation_info.amount_by_percent,
                decimals=decimals,
                wei=True
            )
        else:
            amount_from = balance

        return OperationProposal(
            from_token=from_token,
            amount_from=amount_from
        )

    async def compute_min_destination_amount(
        self,
        operation_proposal: OperationProposal,
        min_to_amount: int,
        operation_info: OperationInfo,
        is_to_token_price_wei: bool = False
    ) -> OperationProposal:
        """
        Compute the minimum destination amount for a swap proposal.

        Args:
            operation_proposal (OperationProposal): The initial operation proposal.
            min_to_amount (int): The minimum amount of the destination token.
            operation_info (OperationInfo): Information about the operation.
            is_to_token_price_wei (bool, optional): Whether the price of the destination token is in wei. Defaults to False.

        Returns:
            SwapProposal: The updated swap proposal with the minimum destination amount.
        """

        if not operation_proposal.to_token:
            operation_proposal.to_token = ContractsFactory.get_contract(
                network_name=self.client.network.name,
                token_symbol=operation_info.to_token_name
            )

        decimals = await self.client.contract.get_decimals(
            contract=operation_proposal.to_token
        )

        min_amount_out = TokenAmount(
            amount=float(min_to_amount) * (1 - operation_info.slippage / 100),
            decimals=decimals,
            wei=is_to_token_price_wei
        )

        return OperationProposal(
            from_token=operation_proposal.from_token,
            amount_from=operation_proposal.amount_from,
            to_token=operation_proposal.to_token,
            min_amount_to=min_amount_out
        )
# endregion Base class for actions
