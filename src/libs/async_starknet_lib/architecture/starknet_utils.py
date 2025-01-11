import hashlib
import random
import bip32
import bip39

from aiohttp import ClientSession
from aiohttp_proxy import ProxyConnector
from hdwallet import (HDWallet, BIP44HDWallet)
from hdwallet.cryptocurrencies import EthereumMainnet
from starknet_py.hash.utils import private_to_stark_key
from starknet_py.hash.address import compute_address
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_errors import ClientError as StarkClientError
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.constants import EC_ORDER
from starknet_py.serialization import TupleDataclass
from starknet_py.cairo.felt import decode_shortstring

from helpers.get_rpcs import get_all_rpcs

from .logger import console_logger
from ..data.config import (
    get_base_path, 
    get_class_hashes
)
from ..models.others import (
    StarkAccount, 
    WalletType
)
from ..models.proxy_manager import ProxyManager
from ..utils.helpers import normalize_non_evm_hex_value


async def mod(a: int, b: int) -> int:
    result = a % b
    return result if result >= 0 else b + result


async def ensure_bytes(seed):
    if isinstance(seed, str):
        if seed.startswith('0x'):
            seed = seed[2:]
        return bytes.fromhex(seed)
    elif isinstance(seed, bytes):
        return seed
    else:
        return


async def sha256_num(data):
    if isinstance(data, str):
        data = data.encode()
    h = hashlib.sha256(data)
    return int.from_bytes(h.digest(), byteorder='big')


async def number_to_var_bytes_be(n):
    hex_string = format(n, 'x')
    if len(hex_string) % 2 != 0:
        hex_string = '0' + hex_string
    return bytes.fromhex(hex_string)


async def _grind_key(seed) -> str | None:
    bytes_seed = await ensure_bytes(seed)
    sha256mask = 2 ** 256
    limit = sha256mask - await mod(sha256mask, EC_ORDER)

    for i in range(100001):
        key = await sha256_num(bytes_seed + await number_to_var_bytes_be(i))
        if key < limit:
            return hex(await mod(key, EC_ORDER))

    console_logger.error('grindKey is broken: tried 100k vals')
    return


class StarknetNodeClient:
    def init_node_client(
        self,
        proxy: str | None = None,
        check_proxy: bool = False
    ) -> FullNodeClient:
        self.proxy = ProxyManager.init_proxy(proxy, check_proxy)

        if self.proxy:
            connector = ProxyConnector.from_url(self.proxy)
            self.session = ClientSession(connector=connector)

        else:
            self.session = None

        client = FullNodeClient(
            node_url=random.choice(get_all_rpcs('Starknet')),
            session=self.session
        )

        return client
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.proxy:
            await self.session.close()


class StarkUtils(StarknetNodeClient):
    def __init__(
        self,
        mnemonic: str,
        proxy: str = '',
        check_proxy: bool = False
    ):
        self.mnemonic = mnemonic
        self.node_client = self.init_node_client(proxy, check_proxy)
        
    async def __aexit__(self, exc_type, exc, tb):
        if self.proxy:
            await self.session.close()

    async def get_account(self) -> StarkAccount | None:
        account_retrieval_methods = [
            self._get_argent_account, 
            self._get_braavos_account
        ]

        for account_method in account_retrieval_methods:
            account = await account_method()
            if account:
                return account

        return StarkAccount(address='Account not found', mnemonic=self.mnemonic)
    
    @staticmethod
    def get_first_element_from_data(
        info: int | TupleDataclass | tuple | dict
    ) -> int | float | str | bool:
        if isinstance(info, int) or isinstance(info, str):
            return info
        elif isinstance(info, TupleDataclass):
            return info.as_tuple()[0]
        elif isinstance(info, tuple):
            return info[0]
        elif isinstance(info, dict):
            return list(info.values())[0]
    
    @staticmethod
    def get_text_from_decimal(
        info: int | TupleDataclass | tuple | dict
    ) -> str | None:
        info = StarkUtils.get_first_element_from_data(info)
        if isinstance(info, str) and info.isdigit():
            info = int(info)
        return str(decode_shortstring(info)).replace('\0', '').strip()

    async def _get_private_argent(self) -> str:
        hdkey1 = BIP44HDWallet(
            cryptocurrency=EthereumMainnet).from_mnemonic(self.mnemonic)
        hdkey2 = HDWallet(
            cryptocurrency=EthereumMainnet).from_seed(hdkey1.private_key())
        child_node = hdkey2.from_path(get_base_path())

        private_key = await _grind_key(child_node.private_key())
        if private_key:
            private_key = normalize_non_evm_hex_value(private_key)

        return private_key

    async def _get_private_braavos(self) -> str:
        seed = bip39.phrase_to_seed(self.mnemonic)
        hd_key = bip32.BIP32.from_seed(seed)
        derived = hd_key.get_privkey_from_path(get_base_path())
        
        private_key = await _grind_key('0x' + derived.hex())
        if private_key:
            private_key = normalize_non_evm_hex_value(private_key)

        return private_key

    async def _get_argent_account(self) -> str:
        private_key = await self._get_private_argent()
        public_key = private_to_stark_key(int(private_key, 16))
        
        argent_computing_address_dict = {
            263: compute_address(
                class_hash=get_class_hashes('argentx_implementation_cairo_2_6_3'),
                constructor_calldata=[
                    public_key,
                    0
                ],
                salt=public_key
            ),
            243: compute_address(
                class_hash=get_class_hashes('argentx_implementation_cairo_2_4_3'),
                constructor_calldata=[
                    public_key,
                    0
                ],
                salt=public_key
            ),
            1: compute_address(
                class_hash=get_class_hashes('argentx_implementation_cairo_2_0_0'),
                constructor_calldata=[
                    public_key,
                    0
                ],
                salt=public_key
            ),
            0: compute_address(
                class_hash=get_class_hashes('argentx_proxy'),
                constructor_calldata=[
                    get_class_hashes('argentx_implementation'),
                    get_selector_from_name("initialize"),
                    2,
                    public_key,
                    0
                ],
                salt=public_key
            )
        }
        
        for cairo_version in argent_computing_address_dict:
            try:
                address = argent_computing_address_dict[cairo_version]
                address = normalize_non_evm_hex_value(hex(address))
                
                class_hash = await self.node_client.get_class_hash_at(address)
                if class_hash:
                    return StarkAccount(self.mnemonic, private_key, address, WalletType.ARGENT)

            except StarkClientError as e:
                error = str(e)
                if 'Contract not found.' in error:
                    cairo_version += 1
        
        return None

    async def _get_braavos_account(self) -> int:
        private_key = await self._get_private_braavos()
        public_key = private_to_stark_key(int(private_key, 16))
        
        braavos_computing_address_dict = {
            251: compute_address(
                class_hash=get_class_hashes('braavos_implementation_cairo_2_5_1'),
                constructor_calldata=[
                    public_key,
                    0
                ],
                salt=public_key
            ),
            0: compute_address(
                class_hash=get_class_hashes('braavos_proxy'),
                constructor_calldata=[
                    get_class_hashes('braavos_implementation'),
                    get_selector_from_name("initializer"),
                    1,
                    public_key
                ],
                salt=public_key
            )
        }
        for cairo_version in braavos_computing_address_dict:
            try:
                address = braavos_computing_address_dict[cairo_version]
                address = normalize_non_evm_hex_value(hex(address))
                
                class_hash = await self.node_client.get_class_hash_at(address)
                if class_hash:
                    return StarkAccount(self.mnemonic, private_key, address, WalletType.BRAAVOS)

            except StarkClientError as e:
                error = str(e)
                if 'Contract not found.' in error:
                    cairo_version += 1

        return None