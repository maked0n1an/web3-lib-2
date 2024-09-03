import asyncio
import base64
import hmac
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from urllib.parse import urlencode

from libs.cexs.common.logger import CustomLogger
from libs.cexs.common.models import Cex, LogStatus, OkxCredentials
from libs.pretty_utils import exceptions
from libs.pretty_utils.exceptions import ApiException
from libs.pretty_utils.miscellaneous.http import make_async_request
from libs.pretty_utils.others import TokenSymbol


def get_okx_chain_names():
    return {
        'ethereum': 'ERC20',
        'aptos': 'Aptos',
        'arbitrum': 'Arbitrum One',
        'avalanche': 'Avalanche C-Chain',
        'base': 'Base',
        'bsc': 'BSC',
        'celo': 'CELO',
        'core': 'CORE',
        'fantom': 'Fantom',
        'injective': 'INJ',
        'klay': 'Klaytn',
        'moonbeam': 'Moonbeam',
        'optimism': 'Optimism',
        'op_bnb': 'OPBNB',
        'polygon': 'Polygon',
        'solana': 'Solana',
        'celestia': 'Celestia',
        'zksync': 'zkSync Era',
    }


class OkxPaths:
    API_ENDPOINT = 'https://www.okx.com'

    GET_ASSET_CURRENCIES_V5 = '/api/v5/asset/currencies'
    GET_USER_SUBACCOUNTS_V5 = '/api/v5/users/subaccount/list'
    GET_ACC_BALANCE_V5 = '/api/v5/asset/balances'
    GET_ACC_BALANCE_EU_TYPE_V5 = '/api/v5/account/balance'
    GET_SUBACC_BALANCE_V5 = '/api/v5/asset/subaccount/balances'
    GET_SUBACC_BALANCE_EU_TYPE_V5 = '/api/v5/account/subaccount/balances'
    GET_DEPOSIT_HISTORY_V5 = '/api/v5/asset/deposit-history'
    TRANSFER_V5 = '/api/v5/asset/transfer'
    WITHDRAW_V5 = '/api/v5/asset/withdrawal'


class OkxErrors(str, Enum):
    ADDRESS_NOT_IN_WL = 'Withdrawal address isn\'t on the verified address list'
    INSSUFICIENT_BALANCE = 'Insufficient balance'
    
    def __str__(self) -> str:
        return self.value


class Okx(Cex):
    def __init__(self, credentials: OkxCredentials):
        super().__init__(
            credentials=credentials
        )
        self.logger = CustomLogger(credentials.cex_name)
        self.is_okx_eu_type = credentials.is_okx_eu_type
        
        self.special_tokens = {
            TokenSymbol.USDC_E: TokenSymbol.USDC
        }

    async def withdraw(
        self,
        ccy: str,
        amount: float,
        network_name: str,
        receiver_address: str,
        receiver_account_id: str = ''
    ):
        url = OkxPaths.WITHDRAW_V5
        
        wd_raw_data = await self._get_currencies(ccy)
        okx_chain_names = get_okx_chain_names()
        if network_name not in okx_chain_names:
            return 'Can not withdraw'

        norm_network_name = okx_chain_names[network_name]
        for wd_chain in wd_raw_data['data']:
            if (
                wd_chain['canWd']
                and norm_network_name in wd_chain['chain']
            ):
                okx_network_name = wd_chain['chain']
                break

        await self.transfer_from_subs(ccy=ccy, silent_mode=True)

        if amount == 0.0:
            raise exceptions.ApiClientException('Can`t withdraw zero amount')

        log_args = [receiver_account_id, receiver_address, network_name]
        
        self.logger.log_message(
            *log_args,
            status=LogStatus.INFO,
            message=f'Withdraw {amount} {ccy} to \'{norm_network_name}\'',
        )

        while True:
            network_data = {
                item['chain']: {
                    'can_withdraw': item['canWd'],
                    'min_fee': item['minFee'],
                    'min_withdraw': item['minWd'],
                    'max_withdraw': item['maxWd']
                } for item in wd_raw_data['data']
            }[okx_network_name]

            if not network_data['can_withdraw']:
                self.logger.log_message(
                    *log_args,
                    status=LogStatus.WARNING,
                    message=f"Withdraw to \'{norm_network_name}\' is not active now. Will try again in 1 min...",
                )
                await self.sleep(60)

            min_wd = float(network_data['min_withdraw'])
            max_wd = float(network_data['max_withdraw'])

            if amount <= min_wd or amount >= max_wd:
                raise exceptions.ApiClientException(
                    f"Limit range for withdraw: {min_wd:.4f} {ccy} - {max_wd} {ccy}, your amount: {amount:.4f}")

            amount = amount - float(network_data['min_fee'])

            if amount < float(network_data['min_withdraw']):
                amount = amount + float(network_data['min_fee'])

            body = {
                'ccy': ccy,
                'amt': amount,
                'dest': "4",
                "toAddr": receiver_address,
                "fee": network_data['min_fee'],
                "chain": okx_network_name
            }

            headers = await self._get_headers(
                method="POST",
                request_path=url,
                body=str(body)
            )

            # # ccy = self._check_for_special_tokens(ccy)

            response = await make_async_request(
                method='POST',
                url=OkxPaths.API_ENDPOINT + url,
                data=str(body),
                headers=headers
            )
            error_section = response['msg']
            
            if any(error in error_section for error in OkxErrors):
                is_successfull = False
                status = LogStatus.FAILED
                message = f'{error_section} to withdraw'
            else:
                is_successfull = True
                status = LogStatus.WITHDRAWN
                message = f'Withdrawn {amount} {ccy}. Wait a little for receiving funds'

            self.logger.log_message(
                *log_args,
                status=status,
                message=message,
            )
            
            return is_successfull

    async def wait_deposit_confirmation(
        self,
        ccy: str,
        amount: float,
        network_name: str,
        old_sub_balances: dict,
        check_time: int = 45
    ):
        # ccy = self._check_for_special_tokens(ccy)

        self.logger.log_message(
            status=LogStatus.INFO,
            message=f"Start checking CEX balances"
        )

        while True:
            new_sub_balances = await self._get_cex_balances(ccy=ccy, deposit_mode=True)
            for sub_name, sub_balance in new_sub_balances.items():

                if sub_balance > old_sub_balances[sub_name]:
                    self.logger.log_message(
                        status=LogStatus.DEPOSITED,
                        message=f"{amount} {ccy} in {network_name.capitalize()}",
                    )
                    return True
                else:
                    continue
            else:
                self.logger.log_message(
                    status=LogStatus.WARNING,
                    message=f"Deposit still in progress..."
                )
                await asyncio.sleep(check_time)

    async def transfer_from_subs(
        self,
        ccy: str,
        amount: float = None,
        silent_mode: bool = False
    ):
        result_1 = await self._transfer_from_subaccounts(ccy, amount, silent_mode)
        result_2 = await self._transfer_from_spot_to_funding(ccy)

        return all([result_1, result_2])

    def _check_for_special_tokens(self, ccy: str):
        if ccy in self.special_tokens:
            ccy = self.special_tokens[ccy]

        return ccy

    async def _get_headers(
        self,
        request_path: str,
        method: str = "GET",
        body: str = "",
        params: dict[str, Any] = {}
    ):
        try:
            timestamp = datetime.now(timezone.utc).strftime(
                '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            key = bytes(self.credentials.api_secret, encoding='utf-8')

            if params:
                request_path = f"{request_path}?{urlencode(params)}"

            message = bytes(timestamp + method + request_path +
                            body, encoding='utf-8')
            encoded_signature = hmac.new(
                key, message, digestmod='sha256').digest()
            decoded_signature = base64.b64encode(encoded_signature).decode()

            return {
                "Content-Type": "application/json",
                "OK-ACCESS-KEY": self.credentials.api_key,
                "OK-ACCESS-SIGN": decoded_signature,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": self.credentials.api_passphrase,
                "x-simulated-trading": "0"
            }
        except Exception as error:
            raise ApiException(f"Bad headers for OKX request: {error}")

    async def _get_sub_list(self):
        url = OkxPaths.GET_USER_SUBACCOUNTS_V5
        headers = await self._get_headers(request_path=url)

        return await make_async_request(
            url=OkxPaths.API_ENDPOINT + url,
            headers=headers
        )

    async def _get_currencies(self, ccy: str = 'ETH') -> list[dict]:
        # ccy = self._check_for_special_tokens(ccy)

        url = OkxPaths.GET_ASSET_CURRENCIES_V5 + f'?ccy={ccy}'
        headers = await self._get_headers(request_path=url)

        return await make_async_request(
            url=OkxPaths.API_ENDPOINT + url,
            headers=headers
        )

    async def _get_main_acc_balance(
        self,
        ccy: str,
        deposit_mode: bool = False
    ) -> float:
        if self.is_okx_eu_type and deposit_mode:
            url = OkxPaths.GET_ACC_BALANCE_EU_TYPE_V5

        else:
            url = OkxPaths.GET_ACC_BALANCE_V5

        params = {
            'ccy': ccy
        }
        headers = await self._get_headers(url, params=params)

        response = await make_async_request(
            url=OkxPaths.API_ENDPOINT + url,
            headers=headers,
            params=params
        )

        if not response:
            return 0

        if self.is_okx_eu_type and deposit_mode:
            balance_data = (
                response[0]['details']
                if response[0]['details'] else {}
            )
            for bal in balance_data:
                if bal['ccy'] == ccy:
                    return float(bal['availBal'])
        else:
            return float(response[0]['availBal'])

    async def _get_sub_acc_balance(
        self,
        sub_name: str,
        ccy: str
    ) -> float:
        if self.is_okx_eu_type:
            url = OkxPaths.GET_SUBACC_BALANCE_EU_TYPE_V5
            url += f'?subAcct={sub_name}'

        else:
            url = OkxPaths.GET_SUBACC_BALANCE_V5
            url += f'?subAcct={sub_name}&ccy={ccy}'

        headers = await self._get_headers(url)
        response = await make_async_request(
            url=OkxPaths.API_ENDPOINT + url,
            headers=headers
        )

        if not response['data']:
            return 0

        if self.is_okx_eu_type:
            balance_data = (
                response['data'][0]['details']
                if response['data'][0]['details'] else {}
            )
            for bal in balance_data:
                if bal['ccy'] == ccy:
                    return float(bal['availBal'])
        else:
            return float(response['data'][0]['availBal'])

    async def _get_cex_balances(self, ccy: str = 'ETH', deposit_mode: bool = False):
        # ccy = self._check_for_special_tokens(ccy)

        balances = {}

        sub_list = await self._get_sub_list()
        main_balance = await self._get_main_acc_balance(ccy=ccy, deposit_mode=deposit_mode)

        if main_balance:
            balances['Main CEX Account'] = main_balance
        else:
            balances['Main CEX Account'] = 0

        for sub_data in sub_list['data']:
            sub_name = sub_data['subAcct']

            sub_balance = await self._get_sub_acc_balance(sub_name, ccy)

            if sub_balance:
                balances[sub_name] = sub_balance
            else:
                balances[sub_name] = 0

        return balances

    async def _transfer_from_subaccounts(
        self,
        ccy: str = 'ETH',
        amount: float = None,
        silent_mode: bool = False
    ) -> bool:
        # ccy = self._check_for_special_tokens(ccy)

        if not silent_mode:
            self.logger.log_message(
                status=LogStatus.INFO,
                message=f'Checking subaccounts balance'
            )

        is_empty = True
        sub_list = await self._get_sub_list()
        await self.sleep()

        for sub_data in sub_list['data']:
            sub_name = sub_data['subAcct']

            sub_balance = await self._get_sub_acc_balance(sub_name, ccy)
            amount = amount if amount else sub_balance

            if sub_balance == amount and sub_balance != 0.0:
                is_empty = False
                if not silent_mode:
                    self.logger.log_message(
                        status=LogStatus.FOUND,
                        message=f'{sub_name} | subAccount balance : {sub_balance:.8f} {ccy}'
                    )

                body = {
                    "ccy": ccy,
                    "type": "2",
                    "amt": f"{amount:.10f}",
                    "from": "6" if not self.is_okx_eu_type else "18",
                    "to": "6" if not self.is_okx_eu_type else "18",
                    "subAcct": sub_name
                }

                headers = await self._get_headers(
                    request_path=OkxPaths.TRANSFER_V5,
                    method="POST",
                    body=str(body)
                )

                await make_async_request(
                    method="POST",
                    url=OkxPaths.API_ENDPOINT + OkxPaths.TRANSFER_V5,
                    headers=headers,
                    data=str(body)
                )
                
                if not silent_mode:
                    self.logger.log_message(
                        status=LogStatus.SENT,
                        message=f"Transfer {amount:.8f} {ccy} to main account"
                    )
                    break

        if is_empty and not silent_mode:
            self.logger.log_message(
                status=LogStatus.WARNING,
                message=f'subAccounts balance: 0 {ccy}'
            )

        return True

    async def _transfer_from_spot_to_funding(self, ccy: str = 'ETH') -> bool:
        # ccy = self._check_for_special_tokens(ccy)
        url = OkxPaths.GET_ACC_BALANCE_EU_TYPE_V5
        params = {
            'ccy': ccy.upper()
        }

        headers = await self._get_headers(request_path=url, params=params)
        balance = await make_async_request(
            url=OkxPaths.API_ENDPOINT + url,
            headers=headers,
            params=params
        )
        balance = balance['data'][0]['details']

        for ccy_item in balance:
            if ccy_item['ccy'] == ccy and ccy_item['availBal'] != '0':                
                self.logger.log_message(
                    status=LogStatus.INFO,
                    message=f"Main trading account balance: {ccy_item['availBal']} {ccy}"
                )

                body = {
                    "ccy": ccy,
                    "amt": ccy_item['availBal'],
                    "from": "18",
                    "to": "6"
                }

                headers = await self._get_headers(
                    method="POST",
                    request_path=OkxPaths.TRANSFER_V5,
                    body=str(body)
                )
                await make_async_request(
                    method="POST",
                    url=OkxPaths.API_ENDPOINT + OkxPaths.TRANSFER_V5,
                    headers=headers,
                    data=str(body)
                )

                self.logger.log_message(
                    status=LogStatus.SUCCESS,
                    message=f"Transfer {float(ccy_item['availBal']):.6f} {ccy} to funding account"
                )
                break
            else:
                self.logger.log_message(
                    status=LogStatus.WARNING,
                    message=f"Main trading account balance: 0 {ccy}"
                )
                break

        return True
