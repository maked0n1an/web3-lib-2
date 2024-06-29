import asyncio
import aiohttp

from libs.async_eth_lib.architecture.client import Client
from libs.async_eth_lib.models.others import TokenSymbol

# region To construct tx
class Utils:
    async def get_token_info(client: Client, token_address):
        """
        Fetches and prints information about a token from the blockchain.

        Args:
            client (Client): The blockchain client used to interact with the network.
            token_address (str): The address of the token contract on the blockchain.

        Returns:
            None
        """
        contract = await client.contract.get_token_contract(token=token_address)
        print('name:', await contract.functions.name().call())
        print('symbol:', await contract.functions.symbol().call())
        print('decimals:', await contract.functions.decimals().call())
    
    def to_cut_hex_prefix_and_zfill(self, data: str, length: int = 64):
        """
        Convert the string to lowercase and fill it with zeros to the specified length.

        Args:
            length (int): The desired length of the string after filling.

        Returns:
            str: The modified string.
        """
        return data[2:].zfill(length)
    
    @staticmethod
    def parse_params(
        params: str,
        has_function_signature: bool = True
    ) -> None:
        """
        Parse a string of parameters, optionally printing function signature and memory addresses.

        Args:
            params (str): The string of parameters to parse.
            has_function_signature (bool, optional): Whether to print the function signature (default is True).

        Returns:
            None
        """
        if has_function_signature:
            function_signature = params[:10]
            print('Function signature:', function_signature)
            params = params[10:]

        count = 0
        while params:
            memory_address = hex(count * 32)[2:].zfill(3)
            print(f'{memory_address}: {params[:64]}')
            count += 1
            params = params[64:]
# endregion To construct tx


# region To get prices
class PriceUtils:
    STABLES = {
        TokenSymbol.USDT:   1.0,
        TokenSymbol.USDC:   1.0,
        TokenSymbol.USDC_E: 1.0,
        TokenSymbol.USDV:   1.0
    }
    
    async def get_binance_ticker_price(
        self,
        first_token: str = TokenSymbol.ETH,
        second_token: str = TokenSymbol.USDT
    ) -> float | None:
        first_token = first_token.lstrip('W')
        second_token = second_token.lstrip('W')

        if first_token in self.STABLES and second_token in self.STABLES:
            return 1.0

        async with aiohttp.ClientSession() as session:
            price = await self._get_price_from_binance(session, first_token, second_token)
            if price:
                return price
            else:
                return await self._get_price_from_binance(session, second_token, first_token)
            
    async def _get_price_from_binance(
        self,
        session: aiohttp.ClientSession,
        first_token: str,
        second_token: str
    ) -> float | None:
        first_token, second_token = first_token.upper(), second_token.upper()
        for _ in range(5):
            try:
                response = await session.get(
                    f'https://api.binance.com/api/v3/ticker/price?symbol={first_token}{second_token}')
                if response.status != 200:
                    return None
                result_dict = await response.json()
                if 'price' in result_dict:
                    return float(result_dict['price'])
            except Exception as e:
                await asyncio.sleep(2)
        raise ValueError(
            f'Can not get {first_token}{second_token} price from Binance')