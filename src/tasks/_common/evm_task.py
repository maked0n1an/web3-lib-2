from web3.types import TxParams

from _types.networks import NetworkNames
from src.libs.async_eth_lib.architecture.client import EvmClient
from src.libs.async_eth_lib.data.token_contracts import ContractsFactory
from src.libs.async_eth_lib.models.operation import OperationInfo, OperationProposal
from src.libs.async_eth_lib.models.others import TokenAmount
from src.libs.async_eth_lib.models.params_types import AddressType
from src.tasks._common.utils import PriceUtils


class EvmTask:
    def __init__(self, client: EvmClient):
        self.client = client
        
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
    
    @staticmethod
    async def get_token_info(
        client: EvmClient, 
        token_address: AddressType
    ):
        """
        Fetches and prints information about a token from the blockchain.

        Args:
            client (Client): The blockchain client used to interact with the network.
            token_address (str | Address | ChecksumAddress): The address of the token contract on the blockchain.

        Returns:
            None
        """
        contract = client.contract.get_token_evm_contract(token_address)
        print('name:', await contract.functions.name().call())
        print('symbol:', await contract.functions.symbol().call())
        print('decimals:', await contract.functions.decimals().call())

    def set_all_gas_params(
        self,
        operation_info: OperationInfo,
        tx_params: dict | TxParams
    ) -> dict | TxParams:
        """
        Set gas-related parameters in the transaction parameters based on provided OperationInfo.

        Iterates over gas-related attributes in OperationInfo and invokes corresponding methods on
        self.client.contract to modify tx_params accordingly.

        Args:
            info (OperationInfo): Information about the swap containing gas-related attributes.
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
        token_address: AddressType,
        tx_params: TxParams | dict,
        amount: TokenAmount | None = None,
        is_approve_infinity: bool = False
    ) -> bool:
        """
        Approve spending of a specific amount by a spender on behalf of the owner.

        Args:
            token_address (str | Address | ChecksumAddress): The token address.
            amount (TokenAmount | None): The amount to approve (default is None).
            gas_price (float | None): Gas price for the transaction (default is None).
            gas_limit (int | None): Gas limit for the transaction (default is None).
            is_approve_infinity (bool): Whether to approve an infinite amount (default is True).

        Returns:
            bool: True if the approval is successful, False otherwise.
        """
        balance_wei = await self.client.contract.get_balance(
            token_address=token_address
        )
        if balance_wei <= 0:
            return True

        if not amount or amount.Wei > balance_wei:
            amount.Wei = balance_wei

        approved_wei = await self.client.contract.get_approved_amount(
            token_address=token_address,
            spender_address=tx_params['to'],
        )

        if amount.Wei <= approved_wei:
            return True

        tx_params = self.set_all_gas_params(
            operation_info=operation_info,
            tx_params=tx_params
        )

        receipt = await self.client.contract.approve(
            token_address=token_address,
            tx_params=tx_params,
            amount=amount,
            is_approve_infinity=is_approve_infinity
        )

        return receipt['status']
    
    async def create_operation_proposal(
        self,
        op_info: OperationInfo
    ) -> OperationProposal:
        """
        Create an operation proposal for a given operation information using prices from CEX.
        
        Args:
            - `op_info` (OperationInfo): The operation information.

        Returns:
            - `OperationProposal`: The operation proposal.
        """
        op_proposal = await self.init_operation_proposal(op_info)

        first_price = await PriceUtils.get_cex_price(op_info.from_token_name)
        second_price = await PriceUtils.get_cex_price(op_info.to_token_name)

        min_amount_to_wei = op_proposal.amount_from.Wei \
            * first_price / second_price

        return await self.complete_operation_proposal(
            operation_proposal=op_proposal,
            slippage=op_info.slippage,
            min_to_amount=min_amount_to_wei,
        )

    async def init_operation_proposal(
        self,
        operation_info: OperationInfo
    ) -> OperationProposal:
        """
        Initialize an operation proposal for a given operation information.

        Args:
            - `operation_info` (OperationInfo): Information about the operation.

        Returns:
            - `OperationProposal`: The inited proposal for operation with from_token, to_token and amount_from.
        """
        from_token = ContractsFactory.get_contract(
            network_name=self.client.network.name,
            token_symbol=operation_info.from_token_name
        )

        network_name = operation_info.to_network_name or self.client.network.name
        to_token = ContractsFactory.get_contract(
            network_name=network_name,
            token_symbol=operation_info.to_token_name
        )

        if from_token.is_native_token:
            balance_wei = await self.client.contract.get_balance()
            decimals = self.client.network.decimals
        else:
            balance_wei = await self.client.contract.get_balance(from_token.address)
            decimals = await self.client.contract.get_decimals(from_token)

        if operation_info.amount:
            amount_from_wei = int(operation_info.amount * 10 ** decimals)
        elif operation_info.amount_by_percent:
            amount_from_wei = int(balance_wei * operation_info.amount_by_percent)
        else:
            amount_from_wei = balance_wei

        amount_from = TokenAmount(
            amount=min(amount_from_wei, balance_wei),
            decimals=decimals,
            wei=True
        )

        return OperationProposal(
            from_token=from_token,
            amount_from=amount_from,
            to_token=to_token,
            min_amount_to=None
        )
    
    async def complete_bridge_proposal(
        self,
        operation_proposal: OperationProposal,
        slippage: float,
        dst_network_name: NetworkNames,
    ) -> OperationProposal:
        """
        Compute the minimum destination amount for a operation proposal.

        Args:
            - `operation_proposal` (OperationProposal): The initial operation proposal.
            - `to_token_name` (str): The name of the destination token.
            - `slippage` (float): The slippage percentage.
            - `min_amount_to_wei` (int, optional): The minimum amount of the destination token in wei. Defaults to None.

        Returns:
            - `OperationProposal`: The updated operation proposal with the minimum destination amount.
        """
        dst_client = EvmClient(network_name=dst_network_name)
        min_amount_to = TokenAmount(
            amount=(
                operation_proposal.amount_from.Wei * (1 - slippage / 100)
            ),
            decimals=await dst_client.contract.get_decimals(operation_proposal.to_token),
            wei=True
        )

        operation_proposal.min_amount_to = min_amount_to
        return operation_proposal


    async def complete_operation_proposal(
        self,
        operation_proposal: OperationProposal,
        slippage: float,
        min_amount_to_wei: int | float | None = None,
    ) -> OperationProposal:
        """
        Compute the minimum destination amount for a operation proposal.
        Works only in same network (ex - for swaps, not for bridge!)

        Args:
            - `operation_proposal` (OperationProposal): The initial operation proposal.
            - `to_token_name` (str): The name of the destination token.
            - `slippage` (float): The slippage percentage.
            - `min_amount_to_wei` (int, optional): The minimum amount of the destination token in wei. Defaults to None.

        Returns:
            - `OperationProposal`: The updated operation proposal with the minimum destination amount.
        """
        min_amount_to = TokenAmount(
            amount=(
                min_amount_to_wei 
                or 
                operation_proposal.amount_from.Wei * (1 - slippage / 100)
            ),
            decimals=await self.client.contract.get_decimals(operation_proposal.to_token),
            wei=True
        )

        return OperationProposal(
            from_token=operation_proposal.from_token,
            amount_from=operation_proposal.amount_from,
            to_token=operation_proposal.to_token,
            min_amount_to=min_amount_to
        )