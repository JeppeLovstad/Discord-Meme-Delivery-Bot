from contextlib import asynccontextmanager
import psycopg as pg
import utils.iniparser as iniparser
from sshtunnelmanager import SSHTunnelManager


class PostgreSQLDAL():

    ssh_server = None

    def __init__(self):
        print("init called")
        self.conn = None
        self.postgres_args = self.__get_config__()
    
    @classmethod
    async def create(cls, autocommit=True, ssh_tunnel=None):
        cls = PostgreSQLDAL()
        cls.autocommit = autocommit
        if ssh_tunnel:
            cls.update_args_for_ssh_tunnel(ssh_tunnel)
        await cls.__start__()
        return cls
    
    def update_args_for_ssh_tunnel(self,ssh_tunnel):
        ssh_args = ssh_tunnel.get_ssh_tunnel_address()
        if ssh_args:
            self.postgres_args["host"] = ssh_args[0]
            self.postgres_args["port"] = ssh_args[1]
        else:
            raise Exception("No SSH tunnel address provided")
    
    ## test if connection is established
    async def test(self):
        async with self.get_cursor_async() as cur:
            await cur.execute("select VERSION()")
            async for record in cur:
                print(record)
    
    @asynccontextmanager
    async def get_cursor_async(self):
        if self.conn is None:
            raise Exception("Connection invalid")
        cursor = self.conn.cursor()
        
        yield cursor
        
        if not self.autocommit:
            await self.conn.commit()
    
        await cursor.close()
    
    
    async def __start__(self):
        if self.conn is None:
            del self.postgres_args["use_ssh_tunnel"]
            self.conn = await pg.AsyncConnection.connect(**self.postgres_args, autocommit=self.autocommit)

    def __get_config__(self):
        config = iniparser.getConfigAsDict("POSTGRES")
        if config is None:
            raise Exception(
                "Invalid POSTGRES configuration, must setup POSTGRES in config to use"
            )

        return config

    async def __close__(self):
        try:
            if self.conn is not None:
                await self.conn.close()
            self.conn = None
        except:
            print("Something went wrong while closing database connection")
            
async def run():
    sshman = SSHTunnelManager()
    sshman.start_ssh_tunnel()
    DAL = await PostgreSQLDAL.create(ssh_tunnel=sshman)
    await DAL.test()

if __name__ == "__main__":
    import asyncio
    import sys
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


    asyncio.run(run())
