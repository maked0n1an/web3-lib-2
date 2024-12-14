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
        swap_proposal = await self.compute_source_token_amount(swap_info)

        from_token_price = await PriceUtils.get_cex_price(
            first_token=swap_info.from_token_name
        )
        to_token_price = await PriceUtils.get_cex_price(
            first_token=swap_info.to_token_name
        )

        min_amount_out = float(swap_proposal.amount_from.Ether) \
            * from_token_price \
            / to_token_price

        return await self.compute_min_destination_amount(
            swap_proposal=swap_proposal,
            min_to_amount=min_amount_out,
            swap_info=swap_info
        )

    async def compute_source_token_amount(
        self,
        swap_info: OperationInfo
    ) -> OperationProposal:
        """
        Compute the source token amount for a given swap.

        Args:
            swap_info (SwapInfo): Information about the swap.

        Returns:
            TokenSwapProposal: The prepared proposal for the swap.
        """
        from_token = StarknetTokenContracts.get_token(
            token_symbol=swap_info.from_token_name
        )

        if from_token.is_native_token:
            balance_wei = await self.client.account.get_balance()
            decimals = self.client.network_decimals
        else:
            balance_wei = await self.client.account.get_balance(from_token.address)
            decimals = await self.client.contract.get_decimals(from_token)

        if swap_info.amount:
            amount_from = TokenAmount(
                amount=swap_info.amount,
                decimals=decimals
            )
            if amount_from.Wei > balance_wei:
                amount_from = balance_wei

        elif swap_info.amount_by_percent:
            amount_from = TokenAmount(
                amount=balance_wei * swap_info.amount_by_percent,
                decimals=decimals,
                wei=True
            )
        else:
            amount_from = balance_wei

        return OperationProposal(
            from_token=from_token,
            amount_from=amount_from
        )

    async def compute_min_destination_amount(
        self,
        swap_proposal: OperationProposal,
        min_to_amount: float,
        swap_info: OperationInfo,
        is_to_token_price_wei: bool = False
    ) -> OperationProposal:
        """
        Compute the minimum destination amount for a swap proposal.

        Args:
            swap_proposal (SwapProposal): The initial swap proposal.
            min_to_amount (float): The minimum amount of the destination token.
            swap_info (SwapInfo): Information about the swap.
            is_to_token_price_wei (bool, optional): Whether the price of the destination token is in wei. Defaults to False.

        Returns:
            SwapProposal: The updated swap proposal with the minimum destination amount.
        """

        if not swap_proposal.to_token:
            swap_proposal.to_token = StarknetTokenContracts.get_token(
                token_symbol=swap_info.to_token_name
            )

        decimals = await self.client.contract.get_decimals(
            token=swap_proposal.to_token
        )

        min_amount_out = TokenAmount(
            amount=min_to_amount * (1 - swap_info.slippage / 100),
            decimals=decimals,
            wei=is_to_token_price_wei
        )

        return OperationProposal(
            from_token=swap_proposal.from_token,
            amount_from=swap_proposal.amount_from,
            to_token=swap_proposal.to_token,
            min_amount_to=min_amount_out
        )