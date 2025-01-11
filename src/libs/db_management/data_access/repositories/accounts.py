from ...core.entities import AccountEntity
from ...data_access.repositories._generic import GenericSqlRepository


class AccountRepository(GenericSqlRepository[AccountEntity]):
    pass
