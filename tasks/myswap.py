from starknet_py.net.client_models import TransactionExecutionStatus

from libs.async_starknet_lib.architecture.client import StarknetClient
from libs.async_starknet_lib.data.token_contracts import StarknetTokenContracts
from libs.async_starknet_lib.models.contract import RawContract
from libs.async_starknet_lib.utils.decorators import (
    validate_liquidity_pools,
    validate_operation_tokens
)
from libs.async_starknet_lib.models.operation import OperationInfo
from libs.async_starknet_lib.models.others import (
    LogStatus,
    TokenAmount,
    TokenSymbol
)
from tasks._common.starknet_task import StarknetTask


class MySwapSettings:
    AVAILABLE_FOR_SWAP = [
        TokenSymbol.USDC,
        TokenSymbol.DAI,
        TokenSymbol.USDT,
        TokenSymbol.WBTC,
        TokenSymbol.ETH
    ]

    AVAILABLE_FOR_D_W = [
        TokenSymbol.ETH + TokenSymbol.USDC,
        TokenSymbol.DAI + TokenSymbol.ETH,
        TokenSymbol.ETH + TokenSymbol.USDT,
    ]


class MySwap(StarknetTask):
    def __init__(self, client: StarknetClient):
        super().__init__(client)
        self.__router_contract = RawContract(
            title='MySwap Router',
            address=0x10884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28,
            abi_path=('data', 'abis', 'myswap', 'router_abi.json')
        )
        self.__pool_ids = {
            TokenSymbol.ETH + TokenSymbol.USDC: 1,
            TokenSymbol.ETH + TokenSymbol.DAI: 2,
            TokenSymbol.ETH + TokenSymbol.USDT: 4,
            TokenSymbol.DAI + TokenSymbol.USDC: 6,
            TokenSymbol.USDC + TokenSymbol.USDT: 5,
        }
        self.__liquidity_map = {
            MySwapSettings.AVAILABLE_FOR_SWAP[0]: {
                'liquidity_token_address': 0x022b05f9396d2c48183f6deaf138a57522bcc8b35b67dee919f76403d1783136,
                'pool_id': 1,
            },
            MySwapSettings.AVAILABLE_FOR_D_W[1]: {
                'liquidity_token_address': 0x07c662b10f409d7a0a69c8da79b397fd91187ca5f6230ed30effef2dceddc5b3,
                'pool_id': 2,
            },
            MySwapSettings.AVAILABLE_FOR_D_W[2]: {
                'liquidity_token_address': 0x041f9a1e9a4d924273f5a5c0c138d52d66d2e6a8bee17412c6b0f48fe059ae04,
                'pool_id': 4,
            }
        }
    
    def _get_pool_id(self, from_token: str, to_token: str):
        pool_id = self.__pool_ids.get(from_token + to_token)
        if pool_id is None:
            pool_id = self.__pool_ids.get(to_token + from_token)
            if pool_id is None:
                self.client.custom_logger.log_message(
                    LogStatus.ERROR,
                    f"Pool {from_token} <-> {to_token} not found "
                )
                return None
        return pool_id

    @validate_operation_tokens(MySwapSettings.AVAILABLE_FOR_SWAP, 'swap', 'MySwap')
    async def swap(self, swap_info: OperationInfo) -> bool:
        is_result = False
        pool_id = self._get_pool_id(
            from_token=swap_info.from_token_name,
            to_token=swap_info.to_token_name
        )
        if not pool_id:
            return is_result

        swap_proposal = await self.create_operation_proposal(swap_info)
        from_token_contract = self.client.contract.get_starknet_contract_from_raw(
            contract=swap_proposal.from_token
        )
        router_contract = self.client.contract.get_starknet_contract_from_raw(
            contract=self.__router_contract
        )

        approve_call = from_token_contract.functions['approve'].prepare_call(
            spender=router_contract.address,
            amount=swap_proposal.amount_from.Wei
        )
        swap_call = router_contract.functions['swap'].prepare_call(
            pool_id=pool_id,
            token_from_addr=swap_proposal.from_token.address,
            amount_from=swap_proposal.amount_from.Wei,
            amount_to_min=swap_proposal.min_amount_to.Wei
        )
        try:
            response = await self.client.account.execute_v1(
                calls=[approve_call, swap_call],
                auto_estimate=True
            )

            tx_receipt = await self.client.node_client.wait_for_tx(
                response.transaction_hash
            )

            rounded_amount_from = round(swap_proposal.amount_from.Ether, 5)
            rounded_amount_to = round(swap_proposal.min_amount_to.Ether, 5)

            if tx_receipt.execution_status == TransactionExecutionStatus.SUCCEEDED:
                log_status = LogStatus.SWAPPED
                message = ''
                is_result = True
            else:
                log_status = LogStatus.FAILED
                message = 'Failed swap'

            message += (
                f' {rounded_amount_from} {swap_proposal.from_token.title}'
                f' -> {rounded_amount_to} {swap_proposal.to_token.title}: '
                f'https://starkscan.co/tx/{hex(tx_receipt.transaction_hash)}'
            )
        except Exception as e:
            message = str(e)
            log_status = LogStatus.ERROR
            
        self.client.custom_logger.log_message(log_status,message)

        return is_result

    @validate_liquidity_pools(
        available_pools=MySwapSettings.AVAILABLE_FOR_D_W, 
        op_name='add_liquidity', 
        class_name='MySwap'
    )
    async def add_liquidity(self, liq_info: OperationInfo):
        is_result = False
        pool_name = liq_info.from_token_name + liq_info.to_token_name
        dep_proposal = await self.create_operation_proposal(liq_info)

        from_token_contract = self.client.contract.get_starknet_contract_from_raw(
            contract=dep_proposal.from_token
        )
        to_token_contract = self.client.contract.get_starknet_contract_from_raw(
            contract=dep_proposal.to_token
        )

        router_contract = self.client.contract.get_starknet_contract_from_raw(
            contract=self.__router_contract
        )

        from_token_approve_call = (
            from_token_contract.functions['approve'].prepare_call(
                spender=router_contract.address,
                amount=dep_proposal.amount_from.Wei
            )
        )
        to_token_approve_call = (
            to_token_contract.functions['approve'].prepare_call(
                spender=router_contract.address,
                amount=dep_proposal.min_amount_to.Wei
            )
        )

        add_liquidity_call = (
            router_contract.functions['add_liquidity'].prepare_call(
                a_address=dep_proposal.from_token.address,
                a_amount=dep_proposal.amount_from.Wei,
                a_min_amount=int(dep_proposal.amount_from.Wei *
                                 (1 - liq_info.slippage / 100)),
                b_address=dep_proposal.to_token.address,
                b_amount=dep_proposal.min_amount_to.Wei,
                b_min_amount=dep_proposal.min_amount_to.Wei
            )
        )
        try:
            response = await self.client.account.execute_v1(
                calls=[from_token_approve_call,
                       to_token_approve_call, add_liquidity_call],
                auto_estimate=True
            )

            tx_receipt = await self.client.node_client.wait_for_tx(
                response.transaction_hash
            )

            if tx_receipt.execution_status == TransactionExecutionStatus.SUCCEEDED:
                log_status = LogStatus.DEPOSITED
                message = ''
                is_result = True
                
            else:
                log_status = LogStatus.ERROR
                message = 'Failed deposit: '

            rounded_amount_from = round(dep_proposal.amount_from.Ether, 5)
            rounded_amount_to = round(dep_proposal.min_amount_to.Ether, 5)

            message += (
                f'to \'{pool_name}\' pool '
                f'{rounded_amount_from} {dep_proposal.from_token.title} '
                f'- {rounded_amount_to} {dep_proposal.to_token.title}: '
                f'https://starkscan.co/tx/{hex(tx_receipt.transaction_hash)}'
            )
        except Exception as e:
            log_status = LogStatus.FAILED
            message = str(e)

        self.client.custom_logger.log_message(log_status,message)

        return is_result

    @validate_liquidity_pools(
        available_pools=MySwapSettings.AVAILABLE_FOR_D_W, 
        op_name='withdraw_liquidity', 
        class_name='MySwap'
    )
    async def withdraw_liquidity(self, liq_info: OperationInfo):
        pool_name = liq_info.from_token_name + liq_info.to_token_name
        pool_id = self.__liquidity_map[pool_name]['pool_id']
        lp_token_address = (
            self.__liquidity_map[pool_name]['liquidity_token_address']
        )
        try:
            lp_token_amount_wei = await self.client.account.get_balance(lp_token_address)
            lp_contract = self.client.contract.get_token_starknet_contract(
                address=lp_token_address
            )
            router_contract = self.client.contract.get_starknet_contract_from_raw(
                contract=self.__router_contract
            )

            # calculate min amount tokenA and tokenB
            total_pool_supply = await router_contract.functions['get_total_shares'].call(pool_id)
            total_pool_supply = total_pool_supply.total_shares

            amount_list = await router_contract.functions['get_pool'].call(pool_id)
            token_a_amount = amount_list.pool['token_a_reserves']
            token_b_amount = amount_list.pool['token_b_reserves']

            a_decimals = await self.client.contract.get_decimals(
                token=StarknetTokenContracts.get_token(
                    liq_info.from_token_name
                )
            )
            b_decimals = await self.client.contract.get_decimals(
                token=StarknetTokenContracts.get_token(
                    liq_info.to_token_name
                )
            )

            amount_min_a = TokenAmount(
                amount=int((lp_token_amount_wei / total_pool_supply) * token_a_amount
                           * (1 - liq_info.slippage / 100)),
                decimals=a_decimals,
                wei=True
            )
            amount_min_b = TokenAmount(
                amount=int((lp_token_amount_wei / total_pool_supply) * token_b_amount
                           * (1 - liq_info.slippage / 100)),
                decimals=b_decimals,
                wei=True
            )

            approve_call = lp_contract.functions['approve'].prepare_call(
                spender=router_contract.address,
                amount=lp_token_amount_wei
            )
            withdraw_liquidity_call = router_contract.functions['withdraw_liquidity'].prepare_call(
                pool_id=pool_id,
                shares_amount=lp_token_amount_wei,
                amount_min_a=amount_min_a.Wei,
                amount_min_b=amount_min_b.Wei
            )

            response = await self.client.account.execute_v1(
                calls=[approve_call, withdraw_liquidity_call],
                auto_estimate=True
            )

            tx_receipt = await self.client.node_client.wait_for_tx(
                response.transaction_hash
            )

            if tx_receipt.execution_status == TransactionExecutionStatus.SUCCEEDED:
                log_status = LogStatus.WITHDRAWN
                message = ''
                result = True
            else:
                log_status = LogStatus.ERROR
                message = 'Failed withdraw: '
                result = False

            message += (
                f'from \'{pool_name}\' pool '
                f'{amount_min_a} {liq_info.from_token_name} '
                f'- {amount_min_b} {liq_info.to_token_name}: '
                f'https://starkscan.co/tx/{hex(tx_receipt.transaction_hash)}'
            )

            self.client.custom_logger.log_message(
                status=log_status,
                message=message,
            )
        except Exception as e:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=e
            )

            result = False

        return result