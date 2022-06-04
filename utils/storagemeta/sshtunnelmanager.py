from sshtunnel import SSHTunnelForwarder
import utils.iniparser as iniparser


class SSHTunnelManager():
    
    ##def __init__(self):
    ##    self.ssh_tunnel_args = self.__get_config__()
    
    def __get_config__(self):
        config = iniparser.getConfigAsDict(section="SSH_TUNNEL")
        if not config:
            raise Exception(
                "Invalid SSHTUNNEL configuration, must setup SSHTUNNEL in config to use"
            )

        return  config
    
    def get_ssh_tunnel_address(self):
        if self.ssh_server is not None and self.ssh_server.is_active:
            return self.ssh_server.local_bind_address
        else:
            return None

    def start_ssh_tunnel(self):
        ssh_tunnel_args = self.__get_config__()
        if ssh_tunnel_args is not None:
            
            ssh_address_or_host      =  (ssh_tunnel_args["ssh_host"], int(ssh_tunnel_args["ssh_port"]))
            ssh_pkey                 =  ssh_tunnel_args["ssh_cert_location"]
            ssh_private_key_password =  ssh_tunnel_args["ssh_private_key_password"]
            ssh_username             =  ssh_tunnel_args["ssh_user"]
            remote_bind_address      =  (ssh_tunnel_args["remote_bind_address"],int(ssh_tunnel_args["remote_bind_port"]))
            local_bind_address      =  (ssh_tunnel_args["remote_bind_address"],int(ssh_tunnel_args["remote_bind_port"]))
            
            try:
                self.ssh_server = SSHTunnelForwarder(
                    ssh_address_or_host= ssh_address_or_host,
                    ssh_pkey=ssh_pkey,
                    ssh_private_key_password=ssh_private_key_password,
                    ssh_username=ssh_username,
                    remote_bind_address=remote_bind_address,
                    local_bind_address=local_bind_address
                )

                if self.ssh_server is not None:
                    self.ssh_server.start()


            except Exception as e:
                print(e)
        else:
            print("ssh tunnel disabled or not setup")
            
    def close(self):
        try:
            if self.ssh_server is not None:
                self.ssh_server.close()
        except:
            print("Something went wrong while closing ssh tunnel")
            
            
if __name__ == "__main__":
    ssht = SSHTunnelManager()
    ssht.start_ssh_tunnel()
    print(ssht.get_ssh_tunnel_address())