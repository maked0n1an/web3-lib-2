import asyncio
import json

from data.config import PRIVATE_KEYS
from libs.async_eth_lib.architecture.client import EvmClient
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.models.operation import OperationInfo
from tasks import SyncSwap


async def main():
    client = EvmClient(network=Networks.Ethereum)
    # res = await client.transaction.find_tx_by_function_name(
    #     contract_address='0x32400084C286CF3E17e7B677ea9583e60a000324',
    #     function_name='requestL2Transaction',
    #     address='0x36F302d18DcedE1AB1174f47726E62212d1CcEAD',
    # )
    # print(json.dumps(res, indent=4))
    
    # sync_swap = SyncSwap(client=client)
    # swap_info = OperationInfo(
    #     from_network=Networks.zkSync_Era,
    #     from_token_name='ETH',
    #     to_token_name='USDT',
    #     min_percent=10,
    #     max_percent=20
    # )
    
    # await sync_swap.swap(swap_info)

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())