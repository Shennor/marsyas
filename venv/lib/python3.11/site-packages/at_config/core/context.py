from dataclasses import dataclass
from typing import Protocol

class IATComponent(Protocol):

    async def exec_external_method(
        self,
        reciever: str, 
        methode_name: str, 
        method_args: dict, 
        auth_token: str = None
    ) -> dict: ...

    async def check_external_registered(
        self,
        reciever: str,
    ) -> bool: ...
    

@dataclass(kw_only=True)
class Context:
    component: IATComponent
    auth_token: str = None