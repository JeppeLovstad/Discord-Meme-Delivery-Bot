from abc import ABCMeta
from storageinterface import StorageMeta
import psycopg2 as pg2
from sshtunnel import SSHTunnelForwarder
import utils.iniparser as iniparser

class StorageInPostgres(StorageMeta, metaclass=ABCMeta):
    
    conn = None
    ssh_server = None
    
    def __init__(self):
        postgres_args, ssh_tunnel_args = self.__get_config__()
        if ssh_tunnel_args is not None and ssh_tunnel_args["sshtunnel"]:
            self.setup_ssh_tunnel(postgres_args, ssh_tunnel_args)
            
        self.__setup_storage_method__(postgres_args)

    def __get_config__(self):
        config = iniparser.getConfigAsDict()
        if "POSTGRES" not in config:
            raise Exception("Invalid POSTGRES configuration")
        
        postgres_args = config["POSTGRES"]
        
        if "SSH_TUNNEL" not in config:
            #log: no ssh tunnel setup
            print("no ssh tunnel setup")
        ssh_tunnel_args = config["SSH_TUNNEL"] if "SSH_TUNNEL" in config else None
            
        return postgres_args, ssh_tunnel_args

    def setup_ssh_tunnel(self, postgres_args, ssh_tunnel_args):
        self.ssh_server = SSHTunnelForwarder(
            (ssh_tunnel_args["ssh_host"], int(ssh_tunnel_args["ssh_port"])),
            ssh_pkey=ssh_tunnel_args["ssh_cert_location"], 
            ssh_private_key_password=ssh_tunnel_args["ssh_private_key_password"],
            ssh_username=ssh_tunnel_args["ssh_user"],
            remote_bind_address=(postgres_args["host"], int(postgres_args["port"])),
            local_bind_address=(postgres_args["host"], int(postgres_args["port"]))
            )
        
        ## Need to update port and host if using ssh tunnel
        if self.ssh_server is not None:
                self.ssh_server.start()
                postgres_args["host"] = self.ssh_server.local_bind_host
                postgres_args["port"] = self.ssh_server.local_bind_port
    
    def __setup_storage_method__(self, postgres_args) -> None:
        
        self.conn = pg2.connect(**postgres_args)
    
        cur = self.conn.cursor()

        cur.execute('select * from public."TestTable"')
        print(cur.fetchone())
        
        cur.close()

    def store(self,key: tuple[str, ...], value: object, module:str, server:str = "", channel:str = "", user:str = "", value_type: str = "str") -> bool:
        return True
    
    def retrieve(self, key: tuple[str, ...], module:str, server:str = "", channel:str = "", user:str = "", value_type: str = "") -> object:
        pass

    def delete(self, key: tuple[str, ...], module:str, server:str = "", channel:str = "", user:str = "") -> bool:
        return True

    def store_message(self,key: tuple[str, ...], value: str, module:str, server:str = "", channel:str = "", user:str = "") -> bool:
        return True

    def retrieve_message(self, message_id: int, server:str = "", channel:str = "", user:str = "", limit: int = 10) -> str:
        return ''

    def get_server(self, server_id:int): 
        pass

    def get_channel(self, channel_id:int): 
        pass

    def get_user(self, user_id:int): 
        pass
    
    def close(self): 
        if self.conn is not None:
            self.conn.close()
        if self.ssh_server is not None:
            self.ssh_server.close()
    
if __name__ == "__main__":
    
    dal = StorageInPostgres()
    dal.close()
    