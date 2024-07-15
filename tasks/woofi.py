from web3.types import TxParams

import libs.async_eth_lib.models.exceptions as exceptions
from libs.async_eth_lib.data.token_contracts import ContractsFactory
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.models.contract import RawContract
from libs.async_eth_lib.models.others import LogStatus, ParamsTypes
from libs.async_eth_lib.models.swap import SwapInfo, SwapProposal
from libs.async_eth_lib.models.transaction import TxArgs
from libs.async_eth_lib.utils.helpers import read_json, sleep
from tasks._common.utils import BaseTask

# region Contracts
class WoofiContracts:
    WOOFI_ROUTER_V2_ABI = read_json(
        path=('data', 'abis', 'woofi', 'abi.json')
    )

    contracts_dict = {
        'WooRouterV2': {
            Networks.Arbitrum.name: RawContract(
                title='WooRouterV2_Arbitrum',
                address='0x9aed3a8896a85fe9a8cac52c9b402d092b629a30',
                abi=WOOFI_ROUTER_V2_ABI
            ),
            Networks.Polygon.name: RawContract(
                title='WooRouterV2_Polygon',
                address='0x817Eb46D60762442Da3D931Ff51a30334CA39B74',
                abi=WOOFI_ROUTER_V2_ABI
            ),
            Networks.BSC.name: RawContract(
                title='WooRouterV2_BSC',
                address='0x4f4fd4290c9bb49764701803af6445c5b03e8f06',
                abi=WOOFI_ROUTER_V2_ABI
            )
        },
        'AggregationRouterV5': {
            Networks.Polygon.name: RawContract(
                title='AggregationRouterV5_Polygon',
                address='0x1111111254EEB25477B68fb85Ed929f73A960582',
                abi=read_json(
                    path=('data', 'abis', '1inch', 'router_v5.json')
                )
            )
        }
    }

    @classmethod
    def get_dex_contract(cls, name: str, network: str) -> RawContract | None:
        if name not in cls.contracts_dict:
            raise exceptions.DexNotExists(
                f"This router has not been added to {__class__.__name__}"
            )

        if network in cls.contracts_dict[name]:
            return cls.contracts_dict[name][network]
# endregion Contracts


# region Implementation
class WooFi(BaseTask):
    async def swap(
        self,
        swap_info: SwapInfo
    ) -> str:
        check_message = self.validate_swap_inputs(
            first_arg=self.client.account_manager.network.name,
            second_arg=swap_info.to_network,
            param_type='networks'
        )
        if check_message:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False

        dex_contract = WoofiContracts.get_dex_contract(
            name='WooRouterV2',
            network=self.client.account_manager.network.name
        )

        contract = await self.client.contract.get(contract=dex_contract)
        swap_query = await self.create_swap_query(contract=contract, swap_info=swap_info)

        args = TxArgs(
            fromToken=swap_query.source_token.address,
            toToken=swap_query.target_token.address,
            fromAmount=swap_query.source_amount.Wei,
            minToAmount=swap_query.min_target_amount.Wei,
            to=self.client.account_manager.account.address,
            rebateTo=self.client.account_manager.account.address
        )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI('swap', args=args.get_tuple()),
        )

        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        if not swap_query.source_token.is_native_token:
            await self.approve_interface(
                token_contract=swap_query.source_token,
                spender_address=contract.address,
                amount=swap_query.source_amount,
                tx_params=tx_params
            )
            await sleep(15, 30)
        else:
            tx_params['value'] = swap_query.source_amount.Wei

        tx = await self.client.contract.transaction.sign_and_send(tx_params)
        receipt = await tx.wait_for_tx_receipt(self.client.account_manager.w3)

        if receipt:
            account_network = self.client.account_manager.network
            full_path = account_network.explorer + account_network.TX_PATH
            return (
                f'{swap_query.source_amount.Ether} {swap_query.source_token.title} was swapped to '
                f'{swap_query.min_target_amount.Ether} {swap_query.target_token.title} '
                f'via {dex_contract.title}: '
                f'{full_path + tx.hash.hex()}'
            )

        return (
            f'Failed swap {swap_query.source_amount.Ether} to {swap_query.target_token.title} '
            f'via {dex_contract.title}: '
            f'{full_path + tx.hash.hex()}'
        )

    async def create_swap_query(
        self,
        contract: ParamsTypes.Contract,
        swap_info: SwapInfo
    ) -> SwapProposal:
        swap_query = await self.compute_source_token_amount(swap_info=swap_info)

        to_token = ContractsFactory.get_contract(
            network_name=self.client.account_manager.network.name,
            token_symbol=swap_info.to_token_name
        )

        min_to_amount = await contract.functions.tryQuerySwap(
            swap_query.from_token.address,
            to_token.address,
            swap_query.amount_from.Wei
        ).call()

        return await self.compute_min_destination_amount(
            swap_query=swap_query,
            min_to_amount=min_to_amount,
            swap_info=swap_info
        )
