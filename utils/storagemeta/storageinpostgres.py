from abc import ABCMeta
from storageinterface import StorageMeta
import psycopg as pg
from sshtunnel import SSHTunnelForwarder
import utils.iniparser as iniparser


class StorageInPostgres(StorageMeta, metaclass=ABCMeta):

    conn = None
    ssh_server = None
    postgres_args = None
    ssh_tunnel_args = None
    is_setup = False
    usage = {}

    def __init__(self, module: str = ""):
        self.postgres_args, self.ssh_tunnel_args = self.__get_config__()
        self.module = module
        self.__register_usage__(self.module)
        print("init called")

    async def __aenter__(self):
        if not self.is_setup:
            self.setup_ssh_tunnel(self.ssh_tunnel_args)
            await self.__setup_storage_method__(self.postgres_args)
            self.is_setup = True
        print("enter called")
        return self

    def __get_config__(self):
        config = iniparser.getConfigAsDict()
        if "POSTGRES" not in config:
            raise Exception(
                "Invalid POSTGRES configuration, must setup POSTGRES in config to use"
            )

        postgres_args = config["POSTGRES"]
        ssh_tunnel_args = config["SSH_TUNNEL"] if "SSH_TUNNEL" in config else None

        return postgres_args, ssh_tunnel_args

    def setup_ssh_tunnel(self, ssh_tunnel_args):
        if (
            self.ssh_tunnel_args is not None
            and self.postgres_args is not None
            and self.ssh_tunnel_args["sshtunnel"]
        ):
            try:
                self.ssh_server = SSHTunnelForwarder(
                    (ssh_tunnel_args["ssh_host"], int(ssh_tunnel_args["ssh_port"])),
                    ssh_pkey=ssh_tunnel_args["ssh_cert_location"],
                    ssh_private_key_password=ssh_tunnel_args[
                        "ssh_private_key_password"
                    ],
                    ssh_username=ssh_tunnel_args["ssh_user"],
                    remote_bind_address=(
                        self.postgres_args["host"],
                        int(self.postgres_args["port"]),
                    ),
                    local_bind_address=(
                        self.postgres_args["host"],
                        int(self.postgres_args["port"]),
                    ),
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
        self.conn = await pg.AsyncConnection.connect(**postgres_args)

    ## test if connection is established
    async def test(self):
        if self.conn is not None:
            cur = self.conn.cursor()
            await cur.execute("select VERSION()")
            async for record in cur:
                print(record)
            await cur.close()

    def store(
        self,
        key: tuple[str, ...],
        value: object,
        server: str = "",
        channel: str = "",
        user: str = "",
        value_type: str = "str",
    ) -> bool:
        return True

    def retrieve(
        self,
        key: tuple[str, ...],
        server: str = "",
        channel: str = "",
        user: str = "",
        value_type: str = "",
    ) -> object:
        pass

    def delete(
        self,
        key: tuple[str, ...],
        server: str = "",
        channel: str = "",
        user: str = "",
    ) -> bool:
        return True

    def store_message(
        self,
        key: tuple[str, ...],
        value: str,
        server: str = "",
        channel: str = "",
        user: str = "",
    ) -> bool:
        return True

    def retrieve_message(
        self,
        message_id: int,
        server: str = "",
        channel: str = "",
        user: str = "",
        limit: int = 10,
    ) -> str:
        return ""

    def get_server(self, server_id: int):
        pass

    def get_channel(self, channel_id: int):
        pass

    def get_user(self, user_id: int):
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
                if self.conn is not None:
                    await self.conn.close()
                if self.ssh_server is not None:
                    self.ssh_server.close()
                    is_setup = False
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
