import hmac
import urllib3
from typing import Any
from urllib.parse import urlencode, quote_plus

from .common import exceptions as exc
from .common.logger import CustomLogger
from .common.models import Cex, CexCredentials, LogStatus
from .common.http import make_async_request
from .common.time_and_date import get_unix_timestamp


def get_bybit_chain_names():
    return {
        'Ethereum': 'ERC20',
        'Arbitrum': 'Arbitrum One',
        'Arbitrum_Nova': 'Arbitrum Nova',
        'Avalanche': 'Avalanche C-Chain',
        'Base': 'Base Mainnet',
        'BSC': 'BSC (BEP20)',
        'Celo': 'CELO',
        'Core': 'CORE',
        'Fantom': 'Fantom',
        'Injective': 'INJ',
        'Klay': 'Klaytn',
        'Linea': 'LINEA',
        'Moonbeam': 'Moonbeam',
        'Optimism': 'OP Mainnet',
        'opBNB': 'OPBNB',
        'Polygon': 'Polygon',
        'Solana': 'Solana',
        'Celestia': 'Celestia',
        'zkSync_Era': 'zkSync Era',
        'zkSync_Lite': 'zkSync Lite'
    }


class BybitPaths:
    API_ENDPOINT = 'https://api.bybit.com'

    GET_ACCOUNT_INFO_V5 = "/v5/account/info"
    GET_WALLET_BALANCE_V5 = "/v5/account/wallet-balance"
    GET_COIN_INFO_V5 = '/v5/asset/coin/query-info'
    GET_EXCHANGE_ENTITY_LIST = '/v5/asset/withdraw/vasp/list'
    WITHDRAW_V5 = '/v5/asset/withdraw/create'
    WITHDRAW_V3 = '/spot/v3/private/asset/withdraw/create'


class Bybit(Cex, CustomLogger):
    def __init__(self, credentials: CexCredentials):
        Cex.__init__(self, credentials)
        CustomLogger.__init__(self)

    async def withdraw(self):
        pass

    async def wait_deposit_confirmation(self):
        pass

    async def _transfer_from_subs(self):
        pass

    async def _get_headers(
        self,
        payload: dict[str, Any] = {},
    ):
        try:
            recv_window = str(10000)
            timestamp = get_unix_timestamp()
            secret = bytes(self.credentials.api_secret, encoding='utf-8')

            param_str_1 = bytes(
                timestamp + self.credentials.api_key
                + recv_window + urlencode(payload),
                encoding='utf-8'
            )
            hex_signature = hmac.new(
                secret, param_str_1, digestmod='sha256'
            ).hexdigest()

            # param_str= str(timestamp) + self.credentials.api_key + recv_window + urlencode(payload)
            # hash = hmac.new(bytes(self.credentials.api_secret, "utf-8"), param_str.encode("utf-8"),hashlib.sha256)
            # signature = hash.hexdigest()
            # print(hex_signature)
            # print(signature)

            headers = {
                'X-BAPI-API-KEY': self.credentials.api_key,
                'X-BAPI-SIGN': hex_signature,
                'X-BAPI-SIGN-TYPE': '2',
                'X-BAPI-TIMESTAMP': timestamp,
                'X-BAPI-RECV-WINDOW': recv_window,
                'Content-Type': 'application/json',
            }
            
            return headers

        except Exception as error:
            raise exc.ApiException(
                f"Bad headers for Bybit request: {error}")

    async def _get_currencies(self, ccy: str = 'ETH') -> list[dict]:
        url = BybitPaths.GET_COIN_INFO_V5
        params = {
            'coin': ccy.upper()
        }

        headers = await self._get_headers(params)

        return await make_async_request(
            url=BybitPaths.API_ENDPOINT + url,
            headers=headers,
            params=params
        )
        
    async def _get_exchange_entity(self):
        url = BybitPaths.GET_EXCHANGE_ENTITY_LIST
        headers = await self._get_headers()
        
        return await make_async_request(
            url=BybitPaths.API_ENDPOINT + url,
            headers=headers
        )

    async def withdraw(
        self,
        ccy: str, 
        amount: float,
        network_name: str,
        receiver_address: str,
        receiver_account_id: str = ''
    ):
        url = BybitPaths.WITHDRAW_V5
        
        wd_raw_data = await self._get_currencies(ccy)
        bybit_chain_names = get_bybit_chain_names()
        if network_name not in bybit_chain_names:
            return 'Can not withdraw'
        
        norm_chain_name = bybit_chain_names[network_name]
        raw_data = wd_raw_data['result']['rows'][0]['chains']
        
        for wd_chain in raw_data:
            if (
                wd_chain['chainWithdraw']
                and norm_chain_name == wd_chain['chainType']
            ):
                bybit_chain_name: str = wd_chain['chainType']
                break
            
        if amount == 0.0:
            raise exc.ApiClientException('Can`t withdraw zero amount')
    
        log_args = [receiver_account_id, receiver_address, network_name]

        self.logger.log_message(
            *log_args,
            status=LogStatus.INFO,
            message=f'Withdraw {amount} {ccy} to \'{network_name}\''
        )        
        
        while True:
            network_data = {
                item['chainType']: {
                    'can_wd': bool(item['chainWithdraw']),
                    'min_fee': float(item['withdrawFee']),
                    'min_wd': float(item['withdrawMin']),
                } for item in raw_data
            }[bybit_chain_name]
            
            if not network_data['can_wd']:
                self.logger.log_message(
                    *log_args,
                    status=LogStatus.WARNING,
                    message=f'Withdraw to \'{network_name}\'  is not active now. Will try again in 1 min...'
                )
                await self.sleep(60)
            
            min_wd = float(network_data['min_wd'])
            
            if amount <= min_wd:
                raise exc.ApiClientException(
                    f"Limit range for withdraw: {min_wd:.4f} {ccy}, your amount: {amount:.4f}"
                )
            
            body = {
                'coin': ccy.upper(), #ETH
                'chain': bybit_chain_name.upper(), #Arbitrum One
                'address': receiver_address, #0x0...S
                'amount': str(amount),#0.001
                'api_key': self.credentials.api_key,
                # 'recv_window': 5000,
                'timestamp': get_unix_timestamp(),
            }

            # Create the param str
            param_str = urlencode(
                sorted(body.items(), key=lambda tup: tup[0])
            )

            # Generate the signature
            hash = hmac.new(
                bytes(self.credentials.api_key, "utf-8"),
                param_str.encode("utf-8"),
                digestmod='sha256'
            )
            
            signature = hash.hexdigest()
            sign_real = {
                "sign": signature
            }
            param_str = quote_plus(param_str, safe="=&")
            full_param_str = f"{param_str}&sign={sign_real['sign']}"
            
            url = "https://api.bybit.com/asset/v3/private/withdraw/create"
            headers = {"Content-Type": "application/json"}
            
            body = dict(body, **sign_real)
            urllib3.disable_warnings()
            
            # response = await make_async_request(
            #     method='POST',
            #     url=url,
            #     data=json.dumps(body),
            #     headers=headers
            # )
            
            # amount = amount - float(network_data['min_fee'])
            
            # if amount < float(network_data['min_wd']):
            #     amount = amount + float(network_data['min_fee'])
            
            # entity_list = await self._get_exchange_entity()
            # timestamp = str(int(time.time() * 10 ** 3))
            
            # body = {
            #     'coin': ccy.upper(), #ETH
            #     'chain': bybit_chain_name, #Arbitrum One
            #     'address': receiver_address, #0x0...S
            #     'amount': str(amount),#0.001
            #     'timestamp': timestamp,
            # }
            # headers = await self._get_headers(body)
            
            # response = await make_async_request(
            #     method='POST',
            #     url=BybitPaths.API_ENDPOINT + url,
            #     data=str(body),
            #     headers=headers,
            # )
            
            print(response)
            
            return True