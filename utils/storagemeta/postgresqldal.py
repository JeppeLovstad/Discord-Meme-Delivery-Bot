from contextlib import asynccontextmanager
import psycopg as pg
import utils.iniparser as iniparser



class PostgreSQLDAL():

    def __init__(self):
        print("init called")
        self.conn = None
        self.ssh_server = None
        self.postgres_args, self.ssh_tunnel_args = self.__get_config__()
    
    @classmethod
    async def create(cls, autocommit=True):
        cls = PostgreSQLDAL()
        cls.autocommit = autocommit
        await cls.__start__()
        return cls
    
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
            self.__setup_ssh_tunnel__(self.ssh_tunnel_args)
            await self.__setup_storage_method__(self.postgres_args)

    def __get_config__(self):
        config = iniparser.getConfigAsDict()
        if "POSTGRES" not in config:
            raise Exception(
                "Invalid POSTGRES configuration, must setup POSTGRES in config to use"
            )

        postgres_args = config["POSTGRES"]
        ssh_tunnel_args = config["SSH_TUNNEL"] if "SSH_TUNNEL" in config else None

        return postgres_args, ssh_tunnel_args

    def __setup_ssh_tunnel__(self, ssh_tunnel_args):
        if (
            self.ssh_tunnel_args is not None
            and self.postgres_args is not None
            and self.ssh_tunnel_args["sshtunnel"]
        ):
            try:
                from sshtunnel import SSHTunnelForwarder
            except:
                raise
            
            ssh_address_or_host=(ssh_tunnel_args["ssh_host"], int(ssh_tunnel_args["ssh_port"]))
            ssh_pkey=ssh_tunnel_args["ssh_cert_location"]
            ssh_private_key_password=ssh_tunnel_args["ssh_private_key_password"]
            ssh_username=ssh_tunnel_args["ssh_user"]
            remote_bind_address=(self.postgres_args["host"],int(self.postgres_args["port"]))
            local_bind_address=(self.postgres_args["host"],int(self.postgres_args["port"]))
            
            try:
                self.ssh_server = SSHTunnelForwarder(
                    ssh_address_or_host= ssh_address_or_host,
                    ssh_pkey=ssh_pkey,
                    ssh_private_key_password=ssh_private_key_password,
                    ssh_username=ssh_username,
                    remote_bind_address=remote_bind_address,
                    local_bind_address=local_bind_address
                )

                ## Need to update port and host if using ssh tunnel
                if self.ssh_server is not None:
                    self.ssh_server.start()
                    self.postgres_args["host"] = self.ssh_server.local_bind_host
                    self.postgres_args["port"] = self.ssh_server.local_bind_port

            except:
                print("Could not setup ssh_tunnel")
        else:
            print("ssh tunnel disabled or not setup")

    async def __setup_storage_method__(self, postgres_args) -> None:
        self.conn = await pg.AsyncConnection.connect(**postgres_args, autocommit=self.autocommit)
        
    async def __close__(self):
        try:
            if self.conn is not None:
                await self.conn.close()
            if self.ssh_server is not None:
                self.ssh_server.close()
            self.conn = None
        except:
            print("Something went wrong while closing database connection")
            

async def run():
    DAL = await PostgreSQLDAL.create()
    await DAL.test()

if __name__ == "__main__":
    import asyncio
    import sys
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(run())
