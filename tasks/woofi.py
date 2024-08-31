from web3.types import TxParams

import libs.async_eth_lib.models.exceptions as exceptions
from libs.async_eth_lib.data.token_contracts import ContractsFactory
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.models.contract import RawContract
from libs.async_eth_lib.models.others import LogStatus, ParamsTypes
from libs.async_eth_lib.models.operation import OperationInfo, OperationProposal
from libs.async_eth_lib.models.transaction import TxArgs
from libs.async_eth_lib.utils.helpers import sleep
from tasks._common.utils import BaseTask

# region Contracts
class WoofiContracts:
    WOOFI_ROUTER_V2_ABI_PATH = ('data', 'abis', 'woofi', 'abi.json')

    contracts_dict = {
        'WooRouterV2': {
            Networks.Arbitrum.name: RawContract(
                title='WooRouterV2_Arbitrum',
                address='0x9aed3a8896a85fe9a8cac52c9b402d092b629a30',
                abi_path=WOOFI_ROUTER_V2_ABI_PATH
            ),
            Networks.Polygon.name: RawContract(
                title='WooRouterV2_Polygon',
                address='0x817Eb46D60762442Da3D931Ff51a30334CA39B74',
                abi_path=WOOFI_ROUTER_V2_ABI_PATH
            ),
            Networks.BSC.name: RawContract(
                title='WooRouterV2_BSC',
                address='0x4f4fd4290c9bb49764701803af6445c5b03e8f06',
                abi_path=WOOFI_ROUTER_V2_ABI_PATH
            )
        },
        'AggregationRouterV5': {
            Networks.Polygon.name: RawContract(
                title='AggregationRouterV5_Polygon',
                address='0x1111111254EEB25477B68fb85Ed929f73A960582',
                abi_path=('data', 'abis', '1inch', 'router_v5.json')
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
        swap_info: OperationInfo
    ) -> str:
        check_message = self.validate_inputs(
            first_arg=self.client.network.name,
            second_arg=swap_info.to_network,
            param_type='networks'
        )
        if check_message:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False

        dex_contract = WoofiContracts.get_dex_contract(
            name='WooRouterV2',
            network=self.client.network.name
        )

        contract = await self.client.contract.get(contract=dex_contract)
        swap_query = await self.create_swap_proposal(contract=contract, swap_info=swap_info)

        args = TxArgs(
            fromToken=swap_query.from_token.address,
            toToken=swap_query.to_token.address,
            fromAmount=swap_query.amount_from.Wei,
            minToAmount=swap_query.min_amount_to.Wei,
            to=self.client.account.address,
            rebateTo=self.client.account.address
        )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI('swap', args=args.get_tuple()),
        )

        tx_params = self.set_all_gas_params(
            operation_info=swap_info,
            tx_params=tx_params
        )

        if not swap_query.from_token.is_native_token:
            await self.approve_interface(
                token_contract=swap_query.from_token,
                spender_address=contract.address,
                amount=swap_query.amount_from,
                tx_params=tx_params
            )
            await sleep(15, 30)
        else:
            tx_params['value'] = swap_query.amount_from.Wei

        tx = await self.client.transaction.sign_and_send(tx_params)
        receipt = await tx.wait_for_tx_receipt(self.client.w3)

        if receipt:
            account_network = self.client.network
            full_path = account_network.explorer + account_network.TX_PATH
            return (
                f'{swap_query.amount_from.Ether} {swap_query.from_token.title} was swapped to '
                f'{swap_query.min_amount_to.Ether} {swap_query.to_token.title} '
                f'via {dex_contract.title}: '
                f'{full_path + tx.hash.hex()}'
            )

        return (
            f'Failed swap {swap_query.amount_from.Ether} '
            f'to {swap_query.from_token.title} {swap_query.to_token.title} '
            f'via {dex_contract.title}: '
            f'{full_path + tx.hash.hex()}'
        )

    async def create_swap_proposal(
        self,
        contract: ParamsTypes.Web3Contract,
        swap_info: OperationInfo
    ) -> OperationProposal:
        swap_query = await self.compute_source_token_amount(operation_info=swap_info)

        to_token = ContractsFactory.get_contract(
            network_name=self.client.network.name,
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
            operation_info=swap_info
        )
