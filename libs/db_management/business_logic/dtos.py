from datetime import datetime
from decimal import Decimal


class GeneralDTO:
    repr_attrs_num = 3
    repr_attrs = tuple()
    
    def __repr__(self):
        """Return a string representation of the DTO instance.

        This representation includes the specified attributes in `repr_attrs`
        or the first `repr_attrs_num` attributes from the instance. It is designed
        to avoid loading relationships to prevent unexpected behavior.
        """
        attrs = []
        for idx, attr in enumerate(self.__dict__.keys()):
            if attr in self.repr_attrs or idx < self.repr_attrs_num:
                attrs.append(f'{attr}={getattr(self, attr)}')

        return f'{self.__class__.__name__}({", ".join(attrs)})'
    
    def to_dict(self):
        return {attr: getattr(self, attr) for attr in self.__dict__.keys()}
        

class AccountDTO(GeneralDTO):
    id: int
    account_name: str | None
    evm_address: str
    evm_private_key: str
    next_action_time: datetime | None
    planned_swaps_count: int
    planned_mint_count: int
    planned_lending_count: int
    planned_stake_count: int
    completed: bool
    
    def __init__(
        self, 
        id: int, 
        account_name: str | None,
        evm_address: str, 
        evm_private_key: str,
        next_action_time: datetime | None,
        planned_swaps_count: int,
        planned_mint_count: int,
        planned_lending_count: int,
        planned_stake_count: int,
        completed: bool
    ):
        self.id = id
        self.account_name = str(account_name)
        self.evm_address = str(evm_address)
        self.evm_private_key = str(evm_private_key)
        self.next_action_time = next_action_time
        self.planned_swaps_count = int(planned_swaps_count)
        self.planned_mint_count = int(planned_mint_count)
        self.planned_lending_count = int(planned_lending_count)
        self.planned_stake_count = int(planned_stake_count)
        self.completed = bool(completed)


class BridgeDTO(GeneralDTO):
    account_id: int
    from_network: str
    to_network: str
    src_amount: Decimal | float | int
    src_token: str
    dst_amount: Decimal | float | int
    dst_token: str
    volume_usd: Decimal | float | int
    fee: Decimal | float | int
    fee_in_usd: float
    platform: str
    tx_hash: str
    
    def __init__(
        self,
        account_id: int,
        from_network: str,
        to_network: str,
        src_amount: Decimal | float | int,
        src_token: str,
        dst_amount: Decimal | float | int,
        dst_token: str,
        fee: Decimal | float | int,
        from_token_price: float | int,
        native_token_price: float | int,
        platform: str,
        tx_hash: str
    ):
        self.from_network = str(from_network)
        self.to_network = str(to_network)
        self.src_amount = round(float(src_amount), 6)
        self.src_token = str(src_token)
        self.dst_amount = round(float(dst_amount), 6)
        self.dst_token = str(dst_token)
        self.volume_usd = round(from_token_price * float(src_amount), 6)
        self.fee = round(float(fee), 6)
        self.fee_in_usd = round(native_token_price * float(fee), 6)
        self.platform = str(platform)
        self.tx_hash = str(tx_hash)
        self.account_id = int(account_id)


class SwapDTO(GeneralDTO):
    id: int
    network: str    
    src_amount: float
    src_token: str
    dst_amount: float
    dst_token: str
    volume_usd: float
    fee: float
    fee_in_usd: float
    platform: str
    tx_hash: str
    
    def __init__(
        self,
        id: int,
        network: str,
        src_amount: float,
        src_token: str,
        dst_amount: float,
        dst_token: str,
        volume_usd: float,
        fee: float,
        fee_in_usd: float,
        platform: str,
        tx_hash: str
    ):
        self.id = int(id)
        self.network = str(network)
        self.src_amount = float(src_amount)
        self.src_token = str(src_token)
        self.dst_amount = float(dst_amount)
        self.dst_token = str(dst_token)
        self.volume_usd = round(float(volume_usd), 6)
        self.fee = round(float(fee), 6)
        self.fee_in_usd = round(fee_in_usd, 2)
        self.platform = str(platform)
        self.tx_hash = str(tx_hash)
        