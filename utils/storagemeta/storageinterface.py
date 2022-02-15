import abc


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
    def store_message(self,key: str, value: object, module:str, server:str = "", channel:str = "", user:str = "", value_type: str = "str") -> bool:
        pass
    
    @abc.abstractmethod
    def retrieve_message(self, message_id: int, server:str = "", channel:str = "", user:str = "") -> str:
        pass