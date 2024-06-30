import asyncio

from data.config import PRIVATE_KEYS
from libs.async_eth_lib.architecture.client import Client
from libs.async_eth_lib.data.networks import Networks
from tasks.stargate import Stargate


async def main():
    client = Client(private_key=PRIVATE_KEYS[0], network=Networks.Arbitrum)
    stargate = Stargate(client=client)
    
    action = await stargate.bridge()

if __name__ == '__main__':
    asyncio.run(main())