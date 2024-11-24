import asyncio
from mapperpy import ObjectMapper as Mapper1
from mapper.object_mapper import ObjectMapper as Mapper2
from objectmapper import ObjectMapper as Mapper3

from libs.db_management.business_logic.dtos import AccountDTO 
from libs.db_management.business_logic.uow import ServiceUnitOfWork
from libs.db_management.data_access.entities import AccountEntity


async def main():
    async with ServiceUnitOfWork() as uow:
        result = await uow.accounts.get_by_id(1)
        print(result.value)

        class A:
            name: str
            surname: str

            def __init__(self, name: str = '', surname: str = ''):
                self.name = name
                self.surname = surname

        class B:
            name: str
            surname: str

            def __init__(self, name: str = '', surname: str = ''):
                self.name = name
                self.surname = surname

            def __repr__(self):
                return f'B(name={self.name})'
        
        result = A(name='John', surname='Doe')
        mapper = Mapper2()
        mapper.create_map(A, B)
        dto = mapper.map(result)
        print(dto)
        # mapper = ObjectMapper.from_class(AccountEntity, AccountDTO)
        # mapper = mapper.left_initializers({
        #     "mints": lambda: [],
        #     "swaps": lambda: [],
        #     "stakes": lambda: [],
        #     "bridges": lambda: []
        # })
        # mapper = mapper.custom_mappings({'mints': None, 'swaps': None, 'stakes': None, 'bridges': None})

        # result = await uow.accounts.update(account)
        # print(result)

if __name__ == '__main__':
    asyncio.run(main())