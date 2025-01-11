import time

from web3 import Web3
from web3.types import TxParams
import web3.exceptions as web3_exceptions

from src.libs.async_eth_lib.architecture.client import EvmClient
from src.libs.async_eth_lib.data.token_contracts import (
    ZkSyncEraTokenContracts,
    TokenContractData
)
from src.libs.async_eth_lib.models.contract import RawContract
from src.libs.async_eth_lib.models.others import LogStatus, TokenSymbol
from src.libs.async_eth_lib.models.operation import OperationInfo
from src.libs.async_eth_lib.models.transaction import TxArgs
from src.tasks._common.evm_task import EvmTask
from src.tasks._common.utils import HexUtils, PriceUtils


class SyncSwapSettings:
    SYNCSWAP_SWAP_TOKENS = {
        TokenSymbol.ETH,
        TokenSymbol.USDT,
        TokenSymbol.USDC,
        TokenSymbol.BUSD,
        TokenSymbol.WBTC
    }


class SyncSwap(EvmTask):
    def __init__(self, client: EvmClient):
        super().__init__(client)
        self.__raw_router_contract = RawContract(
            title="SyncSwap Router",
            address="0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295",
            abi_path=("data", "abis", "zksync", "sync_swap", "abi.json")
        )
        self.__liquidity_pools = {
            (TokenSymbol.ETH, TokenSymbol.USDC):
                "0x80115c708e12edd42e504c1cd52aea96c547c05c",
            (TokenSymbol.ETH, TokenSymbol.USDT):
                "0xd3D91634Cf4C04aD1B76cE2c06F7385A897F54D3",
            (TokenSymbol.ETH, TokenSymbol.BUSD):
                "0xad86486f1d225d624443e5df4b2301d03bbe70f6",
            (TokenSymbol.ETH, TokenSymbol.WBTC):
                "0xb3479139e07568ba954c8a14d5a8b3466e35533d",
        }

    async def swap(self, swap_info: OperationInfo) -> bool:
        is_result = False
        swap_proposal = await self.init_operation_proposal(swap_info)
        contract = self.client.contract.get_evm_contract_from_raw(
            self.__raw_router_contract
        )

        if swap_info.from_token_name == TokenSymbol.ETH:
            swap_proposal.from_token = ZkSyncEraTokenContracts.WETH

        if swap_info.to_token_name == TokenSymbol.ETH:
            swap_proposal.to_token = ZkSyncEraTokenContracts.WETH

        from_token_price = await PriceUtils.get_cex_price(swap_info.from_token_name)
        second_token_price = await PriceUtils.get_cex_price(swap_info.to_token_name)

        min_to_amount_wei = swap_proposal.amount_from.Wei * from_token_price \
            / second_token_price

        swap_proposal = await self.complete_operation_proposal(
            operation_proposal=swap_proposal,
            slippage=swap_info.slippage,
            min_amount_to_wei=min_to_amount_wei,
        )

        pool = self.__liquidity_pools.get(
            (swap_info.to_token_name.upper(), swap_info.from_token_name.upper())
        ) or self.__liquidity_pools.get(
            (swap_info.from_token_name.upper(), swap_info.to_token_name.upper())
        )
        if not pool:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=f"{swap_info.from_token_name} -> {swap_info.to_token_name}: not existed pool"
            )
            return is_result

        zfilled_from_token = HexUtils.to_cut_hex_prefix_and_zfill(
            swap_proposal.from_token.address
        )
        zfilled_address = HexUtils.to_cut_hex_prefix_and_zfill(
            self.client.account.address
        )
        tokenIn = (
            TokenContractData.ZERO_ADDRESS
            if swap_info.from_token_name == TokenSymbol.ETH
            else swap_proposal.from_token.address
        )

        params = TxArgs(
            path=[
                TxArgs(
                    steps=[
                        TxArgs(
                            pool=Web3.to_checksum_address(pool),
                            data=(
                                '0x' +
                                zfilled_from_token +
                                zfilled_address +
                                (
                                    "2"
                                    if swap_info.from_token_name == TokenSymbol.ETH
                                    else "1"
                                ).zfill(64)
                            ),
                            callback=TokenContractData.ZERO_ADDRESS,
                            callbackData="0x",
                        ).get_tuple()
                    ],
                    tokenIn=tokenIn,
                    amountIn=swap_proposal.amount_from.Wei,
                ).get_tuple()
            ],
            amountOutMin=swap_proposal.min_amount_to.Wei,
            deadline=int(time.time() + 10 * 60),
        )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI("swap", args=params.get_tuple()),
            maxPriorityFeePerGas=0,
        )

        if swap_info.from_token_name != TokenSymbol.ETH:
            approved = await self.approve_interface(
                operation_info=swap_info,
                token_address=swap_proposal.from_token.address,
                tx_params=tx_params,
                amount=swap_proposal.amount_from,
            )
            if approved:
                self.client.custom_logger.log_message(
                    LogStatus.APPROVED,
                    message=f"{swap_proposal.from_token.title} {swap_proposal.amount_from.Ether}"
                )
                await sleep(8, 20)
            else:
                self.client.custom_logger.log_message(
                    LogStatus.FAILED,
                    message=f"Can not approve"
                )
                return is_result
        else:
            tx_params["value"] = swap_proposal.amount_from.Wei

        try:
            tx_params = self.set_all_gas_params(swap_info, tx_params)

            tx = await self.client.transaction.sign_and_send(tx_params)
            receipt = await tx.wait_for_tx_receipt(self.client.w3)

            account_network = self.client.network
            full_path = account_network.explorer + account_network.TX_PATH
            rounded_amount = round(swap_proposal.amount_from.Ether, 5)
            is_result = receipt['status']

            if is_result:
                log_status = LogStatus.SWAPPED
                message = f''

            else:
                log_status = LogStatus.FAILED
                message = f'Swap '

            message += (
                f'{rounded_amount} {swap_info.from_token_name}'
                f' -> {swap_proposal.min_amount_to} {swap_info.to_token_name}: '
                f'{full_path + tx.hash.hex()}'
            )
        except web3_exceptions.ContractCustomError as e:
            if '0xc9f52c71' in str(e):
                message = 'Try to make slippage more'
            log_status = LogStatus.ERROR
        except Exception as e:
            if 'insufficient funds for gas + value' in str(e):
                message = 'Insufficient funds for gas + value'
            else:
                message = str(e)
            log_status = LogStatus.ERROR

        self.client.custom_logger.log_message(log_status, message)

        return is_result
