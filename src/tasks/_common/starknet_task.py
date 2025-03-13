from src.libs.async_starknet_lib.data.token_contracts import StarknetTokenContracts
from src.libs.async_starknet_lib.models.operation import (
    OperationInfo, OperationProposal, InitOperationProposal
)
from src.libs.async_starknet_lib.models.others import TokenAmount
from src.libs.async_starknet_lib.architecture.client import StarknetClient
from src.tasks._common.utils import PriceUtils


class StarknetTask:
    def __init__(self, client: StarknetClient):
        self.client = client

    async def create_operation_proposal(
        self,
        operation_info: OperationInfo
    ) -> OperationProposal:
        """
        Create an operation proposal for a given operation information using prices from CEX.
        
        Args:
            - `op_info` (OperationInfo): The operation information.

        Returns:
            - `OperationProposal`: The operation proposal.
        """
        operation_proposal = await self.init_operation_proposal(operation_info)

        first_price = await PriceUtils.get_cex_price(operation_info.from_token_name)
        second_price = await PriceUtils.get_cex_price(operation_info.to_token_name)

        min_amount_to_wei = operation_proposal.amount_from.Wei \
            * first_price / second_price

        return await self.complete_operation_proposal(
            init_op_proposal=operation_proposal,
            slippage=operation_info.slippage,
            min_amount_to_wei=min_amount_to_wei
        )

    async def init_operation_proposal(
        self,
        op_info: OperationInfo
    ) -> InitOperationProposal:
        """
        Compute the source token amount for a given swap.

        Args:
            - `operation_info` (OperationInfo): Information about the operation.

        Returns:
            - `OperationProposal`: The inited proposal for operation with from_token, to_token and amount_from.
        """
        from_token, to_token = (
            StarknetTokenContracts.get_token(
                token_symbol=op_info.from_token_name
            ),
            StarknetTokenContracts.get_token(
                token_symbol=op_info.to_token_name
            )
        )

        if from_token.is_native_token:
            balance_wei = await self.client.account.get_balance()
            decimals = self.client.network_decimals
        else:
            balance_wei = await self.client.account.get_balance(from_token.address)
            decimals = await self.client.contract.get_decimals(from_token)

        if op_info.amount:
            amount_from_wei = int(op_info.amount * 10 ** decimals)
        elif op_info.amount_by_percent:
            amount_from_wei = int(balance_wei * op_info.amount_by_percent)
        else:
            amount_from_wei = balance_wei

        amount_from = TokenAmount(
            amount=min(amount_from_wei, balance_wei),
            decimals=decimals,
            wei=True
        )

        return InitOperationProposal(
            from_token=from_token,
            amount_from=amount_from,
            to_token=to_token,
        )

    async def complete_operation_proposal(
        self,
        init_op_proposal: InitOperationProposal,
        slippage: float,
        min_amount_to_wei: int | float | None = None,
    ) -> OperationProposal:
        """
        Compute the minimum destination amount for a operation proposal.

        Args:
            - `operation_proposal` (OperationProposal): The initial operation proposal.
            - `to_token_name` (str): The name of the destination token.
            - `slippage` (float): The slippage percentage.
            - `min_amount_to_wei` (int, optional): The minimum amount of the destination token in wei. Defaults to None.
            ###BIggest error here, works only in same network (ex - for swaps, not for bridge!)

        Returns:
            - `OperationProposal`: The updated operation proposal with the minimum destination amount.
        """
        min_amount_to = TokenAmount(
            amount=(
                min_amount_to_wei 
                or 
                init_op_proposal.amount_from.Wei * (1 - slippage / 100)
            ),
            decimals=await self.client.contract.get_decimals(init_op_proposal.to_token),
            wei=True
        )
        
        return OperationProposal(
            from_token=init_op_proposal.from_token,
            amount_from=init_op_proposal.amount_from,
            to_token=init_op_proposal.to_token,
            min_amount_to=min_amount_to
        )