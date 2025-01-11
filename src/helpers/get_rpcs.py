from typing import List

from user_data._inputs.settings.rpcs import PUBLIC_RPCS
from user_data._inputs.settings._global import ANKR_API_KEY


def add_ankr_rpcs_key(public_rpcs: List[str]) -> List[str]:
    for rpc in public_rpcs:
        if 'rpc.ankr.com' in rpc and ANKR_API_KEY:
            rpc = f'{rpc}/{ANKR_API_KEY}'

    return public_rpcs


def get_all_rpcs(network_name: str) -> List[str]:
    return add_ankr_rpcs_key(PUBLIC_RPCS[network_name])
