from typing import Optional


class DefaultModuleSettings:
    count: int
    index_group: int
    sub_index_group: int
    delay: int | None

class UserModuleSettings(DefaultModuleSettings):
    module_name: str
