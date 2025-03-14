import asyncio
from typing import Literal

from src.libs.async_eth_lib.architecture.client import EvmClient
from src.tasks.bridges.stargate.implementation import Stargate

# from src.libs.async_eth_lib.architecture.client import EvmClient
# from src.libs.async_eth_lib.data.networks import Networks
# from src.libs.async_eth_lib.models.operation import OperationInfo
# from tasks.stargate import Stargate


async def main():
    client = EvmClient(
        private_key='',
        network_name='Arbitrum Nova',
    )
    print(client.network.name)

    # stargate = Stargate(client=client)
    # await stargate.bridge()

if __name__ == '__main__':
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    asyncio.run(main())