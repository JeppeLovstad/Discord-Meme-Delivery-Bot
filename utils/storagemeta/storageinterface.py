import abc
from discord.ext import commands, tasks


class StorageMeta(abc.ABC):
    
    
    @abc.abstractmethod
    def setup_storage_method(self, type:str= "", name: str = "", user: str = "", pasword: str = "", host:str = "", port: str = "") -> None:
        pass
    
    @abc.abstractmethod
    def store(self,key: str, value: object, module:str, server:str = "", channel:str = "", user:str = "", value_type: str = "str") -> bool:
        pass
    
    @abc.abstractmethod
    def retrieve(self, key: str, module:str, server:str = "", channel:str = "", user:str = "", value_type: str = "") -> object:
        pass
    
    @abc.abstractmethod
    def delete(self, key: str, module:str, server:str = "", channel:str = "", user:str = "") -> bool:
        pass
    
    @abc.abstractmethod
    def store_message(self,key: str, value: str, module:str, server:str = "", channel:str = "", user:str = "") -> bool:
        pass
    
    @abc.abstractmethod
    def retrieve_message(self, message_id: int, server:str = "", channel:str = "", user:str = "", limit: int = 10) -> str:
        pass
    
    @abc.abstractmethod
    def get_server(self, server_id:int): 
        pass
    
    @abc.abstractmethod
    def get_channel(self, channel_id:int): 
        pass
    
    @abc.abstractmethod
    def get_user(self, user_id:int): 
        pass