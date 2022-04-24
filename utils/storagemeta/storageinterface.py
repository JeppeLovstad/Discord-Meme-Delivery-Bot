from abc import ABC, abstractmethod
from discord.ext import commands, tasks


class StorageMeta(ABC):
    
    @abstractmethod
    def __init__(self, type:str= "", name: str = "", user: str = "", password: str = "", host:str = "", port: str = ""):
        self.__setup_storage_method__(type, name, user, password, host, port)
    
    @abstractmethod
    def __setup_storage_method__(self, type:str= "", name: str = "", user: str = "", password: str = "", host:str = "", port: str = "") -> None:
        pass
    
    @abstractmethod
    def store(self,key: tuple[str, ...], value: object, module:str, server:str = "", channel:str = "", user:str = "", value_type: str = "str") -> bool:
        pass
    
    @abstractmethod
    def retrieve(self, key: tuple[str, ...], module:str, server:str = "", channel:str = "", user:str = "", value_type: str = "") -> object:
        pass
    
    @abstractmethod
    def delete(self, key: tuple[str, ...], module:str, server:str = "", channel:str = "", user:str = "") -> bool:
        pass
    
    @abstractmethod
    def store_message(self,key: tuple[str, ...], value: str, module:str, server:str = "", channel:str = "", user:str = "") -> bool:
        pass
    
    @abstractmethod
    def retrieve_message(self, message_id: int, server:str = "", channel:str = "", user:str = "", limit: int = 10) -> str:
        pass
    
    @abstractmethod
    def get_server(self, server_id:int): 
        pass
    
    @abstractmethod
    def get_channel(self, channel_id:int): 
        pass
    
    @abstractmethod
    def get_user(self, user_id:int): 
        pass