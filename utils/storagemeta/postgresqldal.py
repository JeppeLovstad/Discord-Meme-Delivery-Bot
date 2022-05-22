import psycopg as pg
import utils.iniparser as iniparser



class PostgreSQLDAL():

    conn = None
    ssh_server = None
    postgres_args = None
    ssh_tunnel_args = None


    def __init__(self):
        self.postgres_args, self.ssh_tunnel_args = self.__get_config__()
        await self.__start__()
    # async def __aenter__(self):
    #     await self.start()
    #     return self
    
    def __start__(self):
        if self.conn is None:
            self.__setup_ssh_tunnel__(self.ssh_tunnel_args)
            self.__setup_storage_method__(self.postgres_args)

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
        
    async def close(self):
        try:
            if self.conn is not None:
                await self.conn.close()
            if self.ssh_server is not None:
                self.ssh_server.close()
            self.conn = None
        except:
            print("Something went wrong while closing database connection")
            



async def get_DAL():
    DAL = PostgreSQLDAL()
                

