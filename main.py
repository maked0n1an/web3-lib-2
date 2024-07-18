import asyncio

from data.config import PRIVATE_KEYS
from libs.async_eth_lib.architecture.client import Client
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.models.swap import OperationInfo
from tasks import Stargate, SpaceFi, Mute, Maverick


async def main():
    client = Client(account_id=2, private_key=PRIVATE_KEYS[0], network=Networks.Arbitrum)
    stargate = Stargate(client=client)
    swap_info = OperationInfo(
        from_token_name='BUSD',
        to_token_name='USDC',
        src_network=Networks.ZkSync,
        min_percent=100,
        max_percent=100,
        slippage=1
    )
    
    client = Client(account_id=1, private_key=PRIVATE_KEYS[0], network=Networks.ZkSync)
    maverick = Maverick(client)
    
    action = await maverick.swap(swap_info)

if __name__ == '__main__':
    asyncio.run(main())