import asyncio

from libs.async_eth_lib.architecture.client import EvmClient
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.models.operation import OperationInfo
from tasks.stargate import Stargate


async def main():
    client = EvmClient(
        private_key=PRIVATE_KEYS[0],
        network=Networks.BSC,
    )

    stargate = Stargate(client=client)
    await stargate.bridge()

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())