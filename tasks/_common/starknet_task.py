from libs.async_starknet_lib.data.token_contracts import StarknetTokenContracts
from libs.async_starknet_lib.models.operation import (
    OperationInfo, OperationProposal
)
from libs.async_starknet_lib.models.others import TokenAmount
from libs.async_starknet_lib.architecture.client import StarknetClient
from tasks._common.utils import PriceUtils


class StarknetTask:
    def __init__(self, client: StarknetClient):
        self.client = client

    async def create_operation_proposal(
        self,
        swap_info: OperationInfo
    ) -> OperationProposal:
        swap_proposal = await self.init_operation_proposal(swap_info)

        first_price = await PriceUtils.get_cex_price(swap_info.from_token_name)
        second_price = await PriceUtils.get_cex_price(swap_info.to_token_name)

        min_amount_to_wei = swap_proposal.amount_from.Wei \
            * first_price / second_price

        return await self.complete_operation_proposal(
            operation_proposal=swap_proposal,
            min_to_amount=min_amount_to_wei,
            swap_info=swap_info
        )

    async def init_operation_proposal(
        self,
        op_info: OperationInfo
    ) -> OperationProposal:
        """
        Compute the source token amount for a given swap.

        Args:
            - `operation_info` (OperationInfo): Information about the operation.

        Returns:
            - `OperationProposal`: The inited proposal for operation with from_token, to_token and amount_from.
        """
        from_token, to_token = (
            StarknetTokenContracts.get_token(
                token_symbol=token_name
            )
            for token_name in (
                op_info.from_token_name,
                op_info.to_token_name
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

        return OperationProposal(
            from_token=from_token,
            amount_from=amount_from,
            to_token=to_token
        )

    async def complete_operation_proposal(
        self,
        operation_proposal: OperationProposal,
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