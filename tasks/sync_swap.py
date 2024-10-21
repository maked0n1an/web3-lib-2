import time

from web3 import Web3
from web3.types import TxParams
import web3.exceptions as web3_exceptions

from libs.async_eth_lib.architecture.client import EvmClient
from libs.async_eth_lib.data.token_contracts import (
    ZkSyncEraTokenContracts,
    TokenContractData
)
from libs.async_eth_lib.models.contract import RawContract
from libs.async_eth_lib.models.others import LogStatus, TokenSymbol
from libs.async_eth_lib.models.operation import OperationInfo
from libs.async_eth_lib.models.transaction import TxArgs
from libs.async_eth_lib.utils.decorators import validate_swap_tokens
from libs.async_eth_lib.utils.helpers import sleep
from tasks._common.evm_task import EvmTask
from tasks._common.utils import Utils


SYNCSWAP_SWAP_TOKENS = {
    TokenSymbol.ETH,
    TokenSymbol.USDT,
    TokenSymbol.USDC,
    TokenSymbol.BUSD,
    TokenSymbol.WBTC
}

class SyncSwap(EvmTask, Utils):
    LIQUIDITY_POOLS = {
        (TokenSymbol.ETH, TokenSymbol.USDC):
            "0x80115c708e12edd42e504c1cd52aea96c547c05c",
        (TokenSymbol.ETH, TokenSymbol.USDT):
            "0xd3D91634Cf4C04aD1B76cE2c06F7385A897F54D3",
        (TokenSymbol.ETH, TokenSymbol.BUSD):
            "0xad86486f1d225d624443e5df4b2301d03bbe70f6",
        (TokenSymbol.ETH, TokenSymbol.WBTC):
            "0xb3479139e07568ba954c8a14d5a8b3466e35533d",
    }
    
    @property
    def raw_router_contract(self):
        return self.__router_contract
    
    def __init__(self, client: EvmClient):
        EvmTask.__init__(client)
        Utils.__init__()
        self.__router_contract = RawContract(
            title="SyncSwap Router",
            address="0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295",
            abi_path=("data", "abis", "zksync", "sync_swap", "abi.json")
        )
    
    @validate_swap_tokens(SYNCSWAP_SWAP_TOKENS)
    async def swap(self, swap_info: OperationInfo) -> bool:
        is_result = False
        contract = await self.client.contract.get(contract=self.raw_router_contract)
        swap_proposal = await self.compute_source_token_amount(operation_info=swap_info)

        is_from_token_eth = swap_info.from_token_name == TokenSymbol.ETH

        if is_from_token_eth:
            swap_proposal.from_token = ZkSyncEraTokenContracts.WETH

        if swap_info.to_token_name == TokenSymbol.ETH:
            swap_proposal.to_token = ZkSyncEraTokenContracts.WETH
        else:
            swap_proposal.to_token = ZkSyncEraTokenContracts.get_token(
                token_symbol=swap_info.to_token_name
            )

        from_token_price = await self.get_binance_price(swap_info.from_token_name)
        second_token_price = await self.get_binance_price(swap_info.to_token_name)

        min_to_amount = float(swap_proposal.amount_from.Ether) * from_token_price \
            / second_token_price

        swap_proposal = await self.compute_min_destination_amount(
            operation_proposal=swap_proposal,
            min_to_amount=min_to_amount,
            operation_info=swap_info
        )

        pool = self.LIQUIDITY_POOLS.get(
            (swap_info.to_token_name.upper(), swap_info.from_token_name.upper())
        ) or self.LIQUIDITY_POOLS.get(
            (swap_info.from_token_name.upper(), swap_info.to_token_name.upper())
        )
        if not pool:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=f"{swap_info.from_token_name} -> {swap_info.to_token_name}: not existed pool"
            )
            return is_result

        zfilled_from_token = self.to_cut_hex_prefix_and_zfill(
            swap_proposal.from_token.address
        )
        zfilled_address = self.to_cut_hex_prefix_and_zfill(
            self.client.account.address
        )
        tokenIn = (
            TokenContractData.ZERO_ADDRESS
            if is_from_token_eth
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
                                    if is_from_token_eth
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
                token_contract=swap_proposal.from_token,
                spender_address=contract.address,
                amount=swap_proposal.amount_from,
                operation_info=swap_info,
                tx_params=tx_params,
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
