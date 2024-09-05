import hmac
from enum import Enum
from urllib.parse import urlencode

from .common import exceptions as exc
from .common.logger import CustomLogger
from .common.models import Cex, CexCredentials, LogStatus
from .common.http import make_async_request
from .common.time_and_date import get_unix_timestamp


def get_bingx_network_names():
    return {
        'Ethereum': 'ERC20',
        'Arbitrum': 'ARBITRUM',
        'Avalanche': 'AVAXC',
        'Base': 'BASE',
        'BSC': 'BEP20',
        'Celo': 'CELO',
        'Core': 'CORE',
        # 'Fantom': 'Fantom',
        # 'Injective': 'INJ',
        # 'Kava': 'KAVAEVM',
        # 'Klay': 'Klaytn',
        'Linea': 'LINEA',
        # 'Manta': 'MANTA',
        # 'Moonbeam': 'MOONBEAM',
        'Optimism': 'OPTIMISM',
        # 'opBNB': 'OPBNB',
        # 'Polygon': 'MATIC',
        'Solana': 'SOL',
        'zkSync_Era': 'ZKSYNCERA'
    }


def get_bing_x_endpoints():
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
        'AssCur_V1': '/openApi/wallets/v1/capital/config/getall',
        'AccBal_V1': '/openApi/spot/v1/account/balance',
        'SAccLst_V1': '/openApi/subAccount/v1/list',
        'SAccBal_V1': '/openApi/subAccount/v1/assets',
        'T_V1': '/openApi/wallets/v1/capital/subAccountInnerTransfer/apply',
        'Wd_V1': '/openApi/wallets/v1/capital/withdraw/apply',
    }


class BingXErrors(str, Enum):
    API_KEY_HAVE_NO_PERMISSION_TO_WD = 'Permission denied as the API key was created without the permission'
    INSSUFICIENT_BALANCE = 'Insufficient balance'

    def __str__(self) -> str:
        return self.value


class BingX(Cex, CustomLogger):
    def __init__(self, credentials: CexCredentials):
        Cex.__init__(self, credentials)
        CustomLogger.__init__(self)

        self.domain_url = "https://open-api.bingx.com"
        self.endpoints = get_bing_x_endpoints()
        self.headers = {
            "Content-Type": "application/json",
            "X-BX-APIKEY": self.credentials.api_key,
        }

    async def withdraw(
        self,
        ccy: str,
        amount: float,
        network_name: str,
        receiver_address: str,
        receiver_account_id: str = ''
    ) -> bool:
        url = self.endpoints['Wd_V1']
        is_successfull = False

        wd_raw_data = await self._get_currencies(ccy)
        if not wd_raw_data:
            self.log_message(
                status=LogStatus.ERROR,
                message='Invalid token symbol, check it'
            )
            return is_successfull

        bing_x_network_names = get_bingx_network_names()
        if network_name not in bing_x_network_names:
            self.log_message(
                status=LogStatus.FAILED,
                message='Can not withdraw, the network isn\'t in config'
            )
            return is_successfull

        bing_x_network_name = bing_x_network_names[network_name]
        await self._transfer_from_subaccounts(ccy=ccy, silent_mode=True)

        if amount == 0.0:
            raise exc.ApiException('Can`t withdraw zero amount, refuel the CEX')

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
            }[bing_x_network_name]

            if not network_data['can_wd']:
                self.log_message(
                    *log_args,
                    status=LogStatus.WARNING,
                    message=f"Withdraw to \'{network_name}\' is not active now. Will try again in 1 min...",
                )
                await self.sleep(60)

            min_wd = float(network_data['min_wd'])
            max_wd = float(network_data['max_wd'])

            if amount < min_wd or amount > max_wd:
                raise exc.ApiException(
                    f"Limit range for withdraw: {min_wd} {ccy} - {max_wd} {ccy}, your amount: {amount}"
                )

            amount += float(network_data['min_fee'])

            if amount < float(network_data['min_wd']):
                amount += float(network_data['min_fee'])

            params = {
                "address": receiver_address,
                "amount": amount,
                "coin": ccy,
                "network": bing_x_network_name,
                "walletType": "1",
            }

            url = self._get_full_url(url, params)

            response = await make_async_request(
                method='POST',
                url=url,
                headers=self.headers
            )
            error_section = response['msg']

            if any(error in error_section for error in BingXErrors):
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
                    continue
            else:
                self.log_message(
                    status=LogStatus.WARNING,
                    message=f"Deposit still in progress..."
                )
                await self.sleep(check_time)

    def _get_sign(self, payload: str = '') -> str:
        try:
            secret_key_bytes = self.credentials.api_secret.encode()
            signature = hmac.new(
                secret_key_bytes, payload.encode(), digestmod='sha256'
            ).hexdigest()

            return signature
        except Exception as error:
            raise exc.ApiException(f"Bad signature for BingX request: {error}")

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
        endpoint = self.endpoints['AssCur_V1']
        url = self._get_full_url(endpoint)

        response = await make_async_request(
            url=url,
            headers=self.headers
        )

        token = {}
        for item in response['data']:
            if item['coin'] == ccy:
                token = item
        return token

    async def _get_sub_list(self) -> dict:
        endpoint = self.endpoints['SAccLst_V1']
        params = {
            "page": 1,
            "limit": 100,
        }

        url = self._get_full_url(endpoint, params)

        return await make_async_request(
            url=url,
            headers=self.headers
        )

    async def _get_main_acc_balances(self) -> dict:
        endpoint = self.endpoints['AccBal_V1']
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
            if balances and balance['asset'] == ccy
        ]

        if ccy_balance:
            return float(ccy_balance[0]['free'])
        raise exc.ApiException(f'Your have not enough {ccy} balance on Binance')

    async def _get_sub_acc_balances(self, sub_uid: str) -> dict:
        endpoint = self.endpoints['SAccBal_V1']
        params = {
            "subUid": sub_uid
        }
        url = self._get_full_url(endpoint, params)

        return await make_async_request(
            url=url,
            headers=self.headers
        )

    async def _get_sub_acc_balance(self, sub_uid: str, ccy: str) -> float:
        balances = await self._get_sub_acc_balances(sub_uid)

        if not balances:
            return 0

        ccy_balance = [
            balance for balance in balances
            if balances and balance['asset'] == ccy
        ]

        if ccy_balance:
            return float(ccy_balance[0]['free'])
        raise exc.ApiException(f'Your have not enough {ccy} balance on BingX')

    async def _get_cex_balances(
        self,
        ccy: str = 'ETH',
    ) -> dict:
        while True:
            try:
                balances = {}

                try:
                    balances['Main CEX Account'] = await self._get_main_acc_balance(ccy)
                except Exception as e:
                    balances['Main CEX Account'] = 0

                sub_list = await self._get_sub_list()
                for sub_data in sub_list['result']:
                    sub_name = sub_data['subAccountString']
                    sub_uid = sub_data['subUid']

                    balances[sub_name] = await self._get_sub_acc_balance(sub_uid, ccy)

                return balances
            except Exception as error:
                if '-1021 Msg: Timestamp for' in str(error):
                    self.log_message(
                        status=LogStatus.WARNING,
                        message=f"Bad timestamp for request. Will try again in 10 second...",
                    )
                    await self.sleep(10)
                else:
                    raise error

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

        for sub_data in sub_list['data']['result']:
            sub_name = sub_data['subAccountString']
            sub_uid = sub_data['subUid']

            sub_balance = await self._get_sub_acc_balance(sub_uid, ccy)
            amount = amount if amount else sub_balance

            if sub_balance == 0.0:  # or sub_balance != amount
                continue

            is_empty = False
            self.log_message(
                status=LogStatus.FOUND,
                message=f'{sub_name} | subAccount balance: {sub_balance} {ccy}'
            )

            body = {
                "amount": amount,
                "coin": ccy,
                "userAccount": sub_uid,
                "userAccountType": 1,
                "walletType": 1
            }

            endpoint = self.endpoints['T_V1']

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
