from abc import ABCMeta
from storageinterface import StorageMeta
import psycopg as pg
import utils.iniparser as iniparser
from postgresqldal import PostgreSQLDAL
from sshtunnelmanager import SSHTunnelManager

class StorageInPostgres(StorageMeta, metaclass=ABCMeta):

    DAL:PostgreSQLDAL 
    usage = {}

    def __init__(self, module: str = ""):
        self.module = module
        self.__register_usage__(self.module)

    async def __aenter__(self):
        await self.__setup_storage_method__()
        return self
    
    async def __setup_storage_method__(self) -> None:
        if not self.DAL:
            self.DAL = await PostgreSQLDAL.create()
    
    async def test(self):
        await self.DAL.test()

    async def store(
        self,
        key: tuple[str, ...],
        value: object,
        server: str = "",
        channel: str = "",
        user: str = "",
        value_type: str = "str",
    ) -> bool:
        return True

    async def retrieve(
        self,
        key: tuple[str, ...],
        server: str = "",
        channel: str = "",
        user: str = "",
        value_type: str = "",
    ) -> object:
        pass

    async def delete(
        self,
        key: tuple[str, ...],
        server: str = "",
        channel: str = "",
        user: str = "",
    ) -> bool:
        return True

    async def store_message(
        self,
        key: tuple[str, ...],
        value: str,
        server: str = "",
        channel: str = "",
        user: str = "",
    ) -> bool:
        return True

    async def retrieve_message(
        self,
        message_id: int,
        server: str = "",
        channel: str = "",
        user: str = "",
        limit: int = 10,
    ) -> str:
        return ""

    async def get_server(self, server_id: int):
        pass

    async def get_channel(self, channel_id: int):
        pass

    async def get_user(self, user_id: int):
        pass

    async def __aexit__(self, *args):
        await self.close()

    def __register_usage__(self, module):
        if module in self.usage:
            self.usage[module] += 1
        else:
            self.usage[module] = 1
            
    def __unregister_usage__(self, module):
        self.usage[module] -= 1
        if self.usage[self.module] == 0:
            del self.usage[module]
            
    async def close(self):
        try:
            self.__unregister_usage__(self.module)
    
            if len(self.usage) == 0:
                if self.DAL is not None:
                    await self.DAL.close()
                if self.ssh_server is not None:
                    self.ssh_server.close()
        except:
            print("Something went wrong while closing database connection")


async def run():
    async with StorageInPostgres("Meme") as dal:
        async with StorageInPostgres("quiz") as dal2:
            await dal.test()
            print(dal.module)
            print(dal.usage)
        await dal2.test()
        print(dal2.usage)


if __name__ == "__main__":
    import asyncio
    import sys
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(run())
