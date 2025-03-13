import asyncio
from datetime import datetime, timezone

from src.libs.db_management.business_logic.uow import ServiceUnitOfWork
from src.libs.db_management.core.dtos import AccountDTO

async def main():
    account = AccountDTO(
        account_name='test',
        evm_private_key='0x'+ 'b'*64,
        evm_address='0x'+ 'b'*40,
        next_action_time=datetime.now(timezone.utc),
        planned_mints_count=1,
        planned_swaps_count=1,
        planned_bridges_count=1,
        planned_stakes_count=1,
        completed=True
    )

    async with ServiceUnitOfWork() as uow:
        await uow.accounts.add(account)
        account.id = 1
        account.planned_stakes_count += 1
        await uow.accounts.update(account)
        

if __name__ == '__main__':
    asyncio.run(main())