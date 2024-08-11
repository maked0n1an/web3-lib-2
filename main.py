import asyncio

from data.config import PRIVATE_KEYS
from libs.async_eth_lib.architecture.client import Client
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.models.operation import OperationInfo
from tasks import SyncSwap


async def main():
    client = Client(account_id=2, private_key=PRIVATE_KEYS[0], network=Networks.ZkSync)
    sync_swap = SyncSwap(client=client)
    swap_info = OperationInfo(
        from_network=Networks.ZkSync,
        from_token_name='ETH',
        to_token_name='USDT',
        min_percent=10,
        max_percent=20
    )
    
    await sync_swap.swap(swap_info)

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())