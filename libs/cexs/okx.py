import base64
import hmac
from enum import Enum
from typing import Any, Optional
from urllib.parse import urlencode

from .common import exceptions as exc
from .common.logger import CustomLogger
from .common.models import Cex, OkxCredentials, LogStatus
from .common.http import make_async_request
from .common.time_and_date import get_izoformat_timestamp


def get_okx_network_names():
    return {
        'Ethereum': 'ERC20',
        'Arbitrum': 'Arbitrum One',
        'Avalanche': 'Avalanche C-Chain',
        'Base': 'Base',
        'BSC': 'BSC',
        'Celo': 'CELO',
        'Core': 'CORE',
        'Fantom': 'Fantom',
        'Injective': 'INJ',
        'Klay': 'Klaytn',
        'Linea': 'Linea',
        'Moonbeam': 'Moonbeam',
        'Optimism': 'Optimism',
        'opBNB': 'OPBNB',
        'Polygon': 'Polygon',
        'Solana': 'Solana',
        'Celestia': 'Celestia',
        'zkSync_Era': 'zkSync Era'
    }


def get_okx_endpoints():
    # Get = Get,
    # Ass = asset,
    # Acc = Account,
    # Cur = Currencies,
    # Bal = Balance,
    # Lst = List
    # SAcc = SubAcc,
    # T = Transfer
    # U = User
    # Wd = Withdraw
    return {
        'AssCur_V5':        '/api/v5/asset/currencies',
        'AccBal_V5':        '/api/v5/asset/balances',
        'AccBal_EU_V5':     '/api/v5/account/balance',
        'SAccLst_V5':         '/api/v5/users/subaccount/list',
        'SAccBal_V5':         '/api/v5/asset/subaccount/balances',
        'SAccBal_EU_V5':         '/api/v5/account/subaccount/balances',
        'T_V5':         '/api/v5/asset/transfer',
        'Wd_V5':         '/api/v5/asset/withdrawal',
    }


class OkxErrors(str, Enum):
    ADDRESS_NOT_IN_WL = 'Withdrawal address isn\'t on the verified address list'
    INSSUFICIENT_BALANCE = 'Insufficient balance'

    def __str__(self) -> str:
        return self.value


class Okx(Cex, CustomLogger):
    def __init__(self, credentials: OkxCredentials):
        Cex.__init__(self, credentials)
        CustomLogger.__init__(self)

        self.is_okx_eu_type = credentials.is_okx_eu_type
        self.special_tokens = {
            'USDC': 'USDC.e'
        }
        self.domain_url = 'https://www.okx.com'
        self.endpoints = get_okx_endpoints()

    async def get_min_dep_details(
        self,
        ccy: str = 'ETH'
    ) -> Optional[dict]:
        networks_data = {}

        dp_raw_data = await self._get_currencies(ccy)
        if not dp_raw_data['data']:
            self.log_message(
                status=LogStatus.ERROR,
                message='Invalid token symbol for deposit, check it'
            )
            return networks_data

        networks_data = {
            item['chain']: {
                'can_dep': item['canDep'],
                'min_dep': item['minDep'],
                'min_confirm': item['minDepArrivalConfirm'],
                'min_confirm_unlock': item['minWdUnlockConfirm']
            } for item in dp_raw_data['data']
        }

        return networks_data

    async def get_min_dep_details_for_network(
        self,
        ccy: str,
        network_name: str,
    ) -> dict:
        dep_network_info = {}
        okx_network_names = get_okx_network_names()

        if network_name not in okx_network_names:
            self.log_message(
                status=LogStatus.FAILED,
                message='Can not deposit, the network isn\'t in config'
            )
            return dep_network_info

        okx_network_name = f'{ccy.upper()}-{okx_network_names[network_name]}'
        networks_data = await self.get_min_dep_details(ccy)

        if (
            okx_network_name not in networks_data
            or not networks_data[okx_network_name]['can_dep']
        ):
            self.log_message(
                status=LogStatus.ERROR,
                message=(
                    f'{ccy} is unavailable to be deposited to \'{network_name}\''
                )
            )
            return dep_network_info
        return networks_data[okx_network_name]

    async def wait_deposit_confirmation(
        self,
        ccy: str,
        amount: str | float,
        network_name: str,
        old_sub_balances: dict,
        check_time: int = 45
    ) -> bool:
        self.log_message(
            status=LogStatus.INFO,
            message=f"Start checking CEX balances"
        )

        while True:
            new_sub_balances = await self._get_cex_balances(ccy, True)
            for sub_name, sub_balance in new_sub_balances.items():

                if sub_balance > old_sub_balances[sub_name]:
                    self.log_message(
                        status=LogStatus.DEPOSITED,
                        message=f"{amount} {ccy} in {network_name}",
                    )
                    return True
                else:
                    self.log_message(
                        status=LogStatus.WARNING,
                        message=f"Deposit still in progress..."
                    )
                    await self.sleep(check_time)

    async def withdraw(
        self,
        ccy: str,
        amount: float,
        network_name: str,
        receiver_address: str,
        receiver_account_id: str = '',
        is_fee_included_in_request: bool = False
    ) -> bool:
        url = self.endpoints['Wd_V5']
        is_successfull = False

        wd_raw_data = (await self._get_currencies(ccy))['data']
        if not wd_raw_data:
            self.log_message(
                status=LogStatus.ERROR,
                message='Invalid token symbol, check it'
            )
            return is_successfull

        okx_network_names = get_okx_network_names()
        if network_name not in okx_network_names:
            self.log_message(
                status=LogStatus.FAILED,
                message='Can not withdraw, the network isn\'t in config'
            )
            return is_successfull

        await self._transfer_from_subaccounts(ccy=ccy, silent_mode=True)
        if amount == 0.0:
            raise exc.ApiException(
                'Can`t withdraw zero amount, refuel the CEX')

        log_args = [receiver_account_id, receiver_address, network_name]

        self.log_message(
            *log_args,
            status=LogStatus.INFO,
            message=f'Withdraw {amount} {ccy} to \'{network_name}\'',
        )

        okx_network_name = f'{ccy.upper()}-{okx_network_names[network_name]}'
        while True:
            network_datas = {
                item['chain']: {
                    'can_wd': item['canWd'],
                    'min_fee': item['minFee'],
                    'min_wd': item['minWd'],
                    'max_wd': item['maxWd']
                } for item in wd_raw_data
            }
            network_data = network_datas[okx_network_name]

            if not network_data['can_wd']:
                self.log_message(
                    *log_args,
                    status=LogStatus.WARNING,
                    message=f"Withdraw to \'{network_name}\' is not active now. Will try again in 1 min...",
                )
                await self.sleep(60)
                continue

            min_wd = float(network_data['min_wd'])
            max_wd = float(network_data['max_wd'])

            if amount < min_wd or amount > max_wd:
                raise exc.ApiException(
                    f"Limit range for withdraw: {min_wd} {ccy} - {max_wd} {ccy}, your amount: {amount}"
                )

            if is_fee_included_in_request:
                amount -= float(network_data['min_fee'])

            if amount < min_wd:
                while amount < min_wd:
                    amount += float(network_data['min_fee'])

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

            response = await make_async_request(
                method='POST',
                url=self.domain_url + url,
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
                message = f'Successfully withdrawn {amount} {ccy} -> \'{network_name}\'. Wait a little for receiving funds'

            self.log_message(
                *log_args,
                status=status,
                message=message,
            )

            return is_successfull

    async def _transfer_from_subaccounts(
        self,
        ccy: str,
        amount: float = None,
        silent_mode: bool = False
    ) -> bool:
        result_1 = await self._transfer_from_subs(ccy, amount, silent_mode)
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
    ) -> dict:
        try:
            timestamp = get_izoformat_timestamp()
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
            raise exc.ApiException(f"Bad headers for OKX request: {error}")

    async def _get_currencies(self, ccy: str = 'ETH') -> list[dict]:
        url = self.endpoints['AssCur_V5'] + f'?ccy={ccy}'
        headers = await self._get_headers(request_path=url)

        return await make_async_request(
            url=self.domain_url + url,
            headers=headers
        )

    async def _get_sub_list(self) -> dict:
        url = self.endpoints['SAccLst_V5']
        headers = await self._get_headers(request_path=url)

        return await make_async_request(
            url=self.domain_url + url,
            headers=headers
        )

    async def _get_main_acc_balance(
        self,
        ccy: str,
    ) -> float:
        if self.is_okx_eu_type:
            url = self.endpoints['AccBal_EU_V5']

        else:
            url = self.endpoints['AccBal_V5']

        params = {
            'ccy': ccy
        }
        headers = await self._get_headers(url, params=params)

        response = await make_async_request(
            url=self.domain_url + url,
            headers=headers,
            params=params
        )

        if not response:
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

    async def _get_sub_acc_balance(
        self,
        sub_name: str,
        ccy: str
    ) -> float:
        if self.is_okx_eu_type:
            url = self.endpoints['SAccBal_EU_V5']
            url += f'?subAcct={sub_name}'

        else:
            url = self.endpoints['SAccBal_V5']
            url += f'?subAcct={sub_name}&ccy={ccy}'

        headers = await self._get_headers(url)
        response = (await make_async_request(
            url=self.domain_url + url,
            headers=headers
        ))['data']

        if not response:
            return 0

        if self.is_okx_eu_type:
            balance_data = (
                response[0]['details']
                if response[0]['details'] else {}
            )
            for bal in balance_data:
                if bal['ccy'] == ccy:
                    return float(bal['availBal'])
        else:
            return float(response[0]['availBal'])

    async def _get_cex_balances(
        self,
        ccy: str = 'ETH',
    ) -> dict:
        balances = {}

        main_balance = await self._get_main_acc_balance(ccy)
        if main_balance:
            balances['Main CEX Account'] = main_balance
        else:
            balances['Main CEX Account'] = 0

        sub_list = await self._get_sub_list()
        for sub_data in sub_list['data']:
            sub_name = sub_data['subAcct']

            sub_balance = await self._get_sub_acc_balance(sub_name, ccy)

            if sub_balance:
                balances[sub_name] = sub_balance
            else:
                balances[sub_name] = 0

        return balances

    async def _transfer_from_subs(
        self,
        ccy: str = 'ETH',
        amount: float = None,
        silent_mode: bool = False
    ) -> bool:
        if not silent_mode:
            self.log_message(
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

            if sub_balance == 0.0:  # or sub_balance != amount
                continue

            is_empty = False
            if not silent_mode:
                self.log_message(
                    status=LogStatus.FOUND,
                    message=f'{sub_name} | subAccount balance : {sub_balance} {ccy}'
                )

            body = {
                "ccy": ccy,
                "type": "2",
                "amt": f"{amount:.10f}",
                "from": "6" if not self.is_okx_eu_type else "18",
                "to": "6" if not self.is_okx_eu_type else "18",
                "subAcct": sub_name
            }

            while True:
                try:
                    headers = await self._get_headers(
                        request_path=self.endpoints['T_V5'],
                        method="POST",
                        body=str(body)
                    )

                    await make_async_request(
                        method="POST",
                        url=self.domain_url + self.endpoints['T_V5'],
                        headers=headers,
                        data=str(body)
                    )

                    break
                except Exception as error:
                    str_err = str(error)
                    # if (
                    #     'the required block confirmations' in str_err
                    # ):
                    #     self.log_message(
                    #         status=LogStatus.WARNING,
                    #         message=(
                    #             f'Deposit not reached the required block confirmations. '
                    #             f'Will try again in 1 min.'
                    #         )
                    #     )
                    #     await self.sleep(60)
                    # else:
                    self.log_message(
                        status=LogStatus.ERROR,
                        message=str_err
                    )
                    return False

            self.log_message(
                status=LogStatus.SENT,
                message=f"Transfer {amount} {ccy} to main account completed"
            )
            if not silent_mode:
                break

        if is_empty and not silent_mode:
            self.log_message(
                status=LogStatus.WARNING,
                message=f'subAccounts balance: 0 {ccy}'
            )

        return True

    async def _transfer_from_spot_to_funding(self, ccy: str = 'ETH') -> bool:
        url = self.endpoints['AccBal_EU_V5']
        params = {
            'ccy': ccy.upper()
        }

        headers = await self._get_headers(request_path=url, params=params)
        balance = await make_async_request(
            url=self.domain_url + url,
            headers=headers,
            params=params
        )
        balance = balance['data'][0]['details']

        for ccy_item in balance:
            if ccy_item['ccy'] == ccy and ccy_item['availBal'] != '0':
                self.log_message(
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
                    request_path=self.endpoints['T_V5'],
                    body=str(body)
                )
                await make_async_request(
                    method="POST",
                    url=self.domain_url + self.endpoints['T_V5'],
                    headers=headers,
                    data=str(body)
                )

                self.log_message(
                    status=LogStatus.SUCCESS,
                    message=f"Transfer {float(ccy_item['availBal']):.6f} {ccy} to funding account"
                )
                break
            else:
                self.log_message(
                    status=LogStatus.WARNING,
                    message=f"Main trading account balance: 0 {ccy}"
                )
                break

        return True
