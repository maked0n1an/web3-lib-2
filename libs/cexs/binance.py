import hmac
from urllib.parse import urlencode
from typing import Optional

from .common import exceptions as exc
from .common.logger import CustomLogger
from .common.models import Cex, CexCredentials, LogStatus
from .common.http import make_async_request
from .common.time_and_date import get_unix_timestamp


def get_binance_network_names():
    return {
        'Ethereum': 'ETH',
        'Arbitrum': 'ARBITRUM',
        'Avalanche': 'AVAXC',
        'Base': 'BASE',
        'BSC': 'BSC',
        'Celo': 'CELO',
        'Core': 'CORE',
        # 'Fantom': 'Fantom',
        # 'Injective': 'INJ',
        'Kava': 'KAVAEVM',
        'Manta': 'MANTA',
        'Moonbeam': 'MOONBEAM',
        'Optimism': 'OPTIMISM',
        'opBNB': 'OPBNB',
        'Polygon': 'MATIC',
        'Solana': 'SOL',
        'zkSync_Era': 'ZKSYNCERA'
    }


class BinanceEndpoints:
    GET_CURRENCIES_V1 = '/sapi/v1/capital/config/getall'
    GET_ACC_BALANCE_V3 = '/sapi/v3/asset/getUserAsset'
    GET_USER_SUBACCOUNTS_V1 = '/sapi/v1/sub-account/list'
    GET_SUBACC_BALANCE_V3 = '/sapi/v3/sub-account/assets'
    # GET_DEPOSIT_HISTORY_V5 = '/api/v5/asset/deposit-history'
    TRANSFER_V1 = "/sapi/v1/sub-account/universalTransfer"
    WITHDRAW_V1 = '/sapi/v1/capital/withdraw/apply'


class Binance(Cex, CustomLogger):
    def __init__(self, credentials: CexCredentials):
        Cex.__init__(self, credentials)
        CustomLogger.__init__(self)

        self.domain_url = 'https://api.binance.com'
        self.headers = {
            "Content-Type": "application/json",
            "X-MBX-APIKEY": self.credentials.api_key,
        }

    async def get_min_dep_details(
        self,
        ccy: str = 'ETH'
    ) -> Optional[dict]:
        networks_data = {}

        dp_raw_data = await self._get_currencies(ccy)
        if not dp_raw_data:
            self.log_message(
                status=LogStatus.ERROR,
                message='Invalid token symbol for deposit, check it'
            )
            return networks_data

        networks_data = {
            item['network']: {
                'can_dep': item['depositEnable'],
                'min_dep': item['depositDust'],
                'min_confirm': item['minConfirm'],
                'min_unlock_confirm': item['unLockConfirm']
            } for item in dp_raw_data['networkList']
        }

        return networks_data

    async def get_min_dep_details_for_network(
        self,
        ccy: str,
        network_name: str,
    ) -> dict:
        dep_network_info = {}
        binance_network_names = get_binance_network_names()

        if network_name not in binance_network_names:
            self.log_message(
                status=LogStatus.FAILED,
                message='Can not deposit, the network isn\'t in config'
            )
            return dep_network_info

        binance_network_name = binance_network_names[network_name]
        networks_data = await self.get_min_dep_details(ccy)

        if (
            binance_network_name not in networks_data
            or not networks_data[binance_network_name]['can_dep']
        ):
            self.log_message(
                status=LogStatus.ERROR,
                message=(
                    f'{ccy} is unavailable to be deposited to \'{network_name}\''
                )
            )
            return dep_network_info
        return networks_data[binance_network_name]

    async def wait_deposit_confirmation(
        self,
        ccy: str,
        amount: float,
        network_name: str,
        old_sub_balances: dict,
        check_time: int = 45
    ) -> bool:
        self.log_message(
            status=LogStatus.INFO,
            message=f"Start checking CEX balances"
        )

        while True:
            new_sub_balances = await self._get_cex_balances(ccy)
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
        is_successfull = False

        wd_raw_data = await self._get_currencies(ccy)
        if not wd_raw_data:
            self.log_message(
                status=LogStatus.ERROR,
                message='Invalid token symbol, check it'
            )
            return is_successfull

        binance_network_names = get_binance_network_names()
        if network_name not in binance_network_names:
            self.log_message(
                status=LogStatus.FAILED,
                message='Can not withdraw, the network isn\'t in config'
            )
            return is_successfull

        binance_network_name = binance_network_names[network_name]
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

        while True:
            network_data = {
                item['network']: {
                    'can_wd': item['withdrawEnable'],
                    'min_fee': item['withdrawFee'],
                    'min_wd': item['withdrawMin'],
                    'max_wd': item['withdrawMax']
                } for item in wd_raw_data['networkList']
            }[binance_network_name]

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

            params = {
                "address": receiver_address,
                "amount": amount,
                "coin": ccy,
                "network": binance_network_name,
            }

            url = self._get_full_url(BinanceEndpoints.WITHDRAW_V1, params)

            response = await make_async_request(
                method='POST',
                url=url,
                headers=self.headers
            )
            # error_section = response['msg']

            # if any(error in error_section for error in OkxErrors):
            #     is_successfull = False
            #     status = LogStatus.FAILED
            #     message = f'{error_section} to withdraw'
            # else:
            is_successfull = True
            status = LogStatus.WITHDRAWN
            message = f'Successfully withdrawn {amount} {ccy} -> \'{network_name}\'. Wait a little for receiving funds'

            self.log_message(
                *log_args,
                status=status,
                message=message,
            )

            return is_successfull

    def _get_sign(self, payload: str = '') -> str:
        try:
            secret_key_bytes = self.credentials.api_secret.encode()
            signature = hmac.new(
                secret_key_bytes, payload.encode(), digestmod='sha256'
            ).hexdigest()

            return signature
        except Exception as error:
            raise exc.ApiException(
                f"Bad signature for Binance request: {error}")

    def _get_url_encoded_params_with_ts(self, params: dict | None = None) -> str:
        if params:
            params_str = urlencode(
                sorted(params.items(), key=lambda tup: tup[0])
            )
        else:
            params_str = ''
        return params_str + "&timestamp=" + get_unix_timestamp()

    def _get_full_url(self, endpoint: str, params: dict = None) -> str:
        url_encoded_params = self._get_url_encoded_params_with_ts(params)
        signature = self._get_sign(url_encoded_params)

        url = (
            f"{self.domain_url}{endpoint}"
            f"?{url_encoded_params}&signature={signature}"
        )

        return url

    async def _get_currencies(self, ccy: str = 'ETH') -> list[dict]:
        endpoint = BinanceEndpoints.GET_CURRENCIES_V1
        url = self._get_full_url(endpoint)

        response = await make_async_request(
            url=url,
            headers=self.headers
        )

        token = {}
        for item in response:
            if item['coin'] == ccy:
                token = item
        return token

    async def _get_sub_list(self) -> dict:
        endpoint = BinanceEndpoints.GET_USER_SUBACCOUNTS_V1
        url = self._get_full_url(endpoint)

        return await make_async_request(
            url=url,
            headers=self.headers
        )

    async def _get_main_acc_balances(self) -> dict:
        endpoint = BinanceEndpoints.GET_ACC_BALANCE_V3
        url = self._get_full_url(endpoint)

        return await make_async_request(
            method='POST',
            url=url,
            headers=self.headers
        )

    async def _get_main_acc_balance(self, ccy: str) -> float:
        balances = await self._get_main_acc_balances()

        ccy_balance = [
            balance for balance in balances
            if balance['asset'] == ccy.upper()
        ]

        if ccy_balance:
            return float(ccy_balance[0]['free'])
        raise exc.ApiException(
            f'Your have not enough {ccy} balance on Binance')

    async def _get_sub_acc_balance(self, sub_email: str) -> dict:
        endpoint = BinanceEndpoints.GET_SUBACC_BALANCE_V3
        params = {
            "email": sub_email
        }
        url = self._get_full_url(endpoint, params)

        return await make_async_request(
            url=url,
            headers=self.headers
        )

    async def _get_cex_balances(
        self,
        ccy: str = 'ETH',
    ) -> dict:
        balances = {}

        try:
            balances['Main CEX Account'] = await self._get_main_acc_balance(ccy)
        except Exception as e:
            balances['Main CEX Account'] = 0

        sub_list = await self._get_sub_list()
        for sub_data in sub_list['subAccounts']:
            sub_name = sub_data['email']
            sub_balances = await self._get_sub_acc_balance(sub_name)
            ccy_sub_balance = [
                balance for balance in sub_balances['balances']
                if balance['asset'] == ccy.upper()
            ]

            if ccy_sub_balance:
                balances[sub_name] = float(ccy_sub_balance[0]['free'])
            else:
                balances[sub_name] = 0

        return balances

    async def _transfer_from_subaccounts(
        self,
        ccy: str = 'ETH',
        amount: float = None,
        silent_mode: bool = False
    ):
        if not silent_mode:
            self.log_message(
                status=LogStatus.INFO,
                message=f'Checking subaccounts balance'
            )

        is_empty = True
        sub_list = await self._get_sub_list()
        await self.sleep()

        for sub_data in sub_list['subAccounts']:
            sub_email = sub_data['email']

            sub_balances = await self._get_sub_acc_balance(sub_email)
            asset_balances = [
                balance for balance in sub_balances['balances']
                if balance['asset'] == ccy.upper()
            ]
            sub_balance = (
                0.0
                if len(asset_balances) == 0
                else float(asset_balances[0]['free'])
            )

            amount = amount if amount else sub_balance

            if sub_balance == 0.0:  # or sub_balance != amount
                continue

            is_empty = False
            self.log_message(
                status=LogStatus.FOUND,
                message=f'{sub_email} | subAccount balance: {sub_balance} {ccy}'
            )

            body = {
                "amount": amount,
                "asset": ccy,
                "fromAccountType": "SPOT",
                "toAccountType": "SPOT",
                "fromEmail": sub_email
            }

            endpoint = BinanceEndpoints.TRANSFER_V1

            while True:
                try:
                    url = self._get_full_url(endpoint, body)

                    await make_async_request(
                        method='POST',
                        url=url,
                        headers=self.headers
                    )

                    break
                except Exception as error:
                    str_err = str(error)

                    if (
                        'not reached the required block confirmations' in str_err
                        or '-9000' in str_err
                    ):
                        self.log_message(
                            status=LogStatus.WARNING,
                            message=(
                                f'Deposit not reached the required block confirmations. '
                                f'Will try again in 1 min.'
                            )
                        )
                        await self.sleep(60)
                    elif '-8012 Msg' in str(error):
                        return True
                    else:
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
