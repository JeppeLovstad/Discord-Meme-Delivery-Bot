import configparser
from os import path,walk


_loaded_config = None

class IniParser():

    config:configparser.ConfigParser = configparser.ConfigParser()
    config_file_name = ""
    config_last_change_time = 0

    def __init__(self):
        self.__updateConfig()
        
    def getConfigAsDict(self, section:str="") -> dict:
        self.__updateConfig()
        _dict = {s:dict(self.config.items(s)) for s in self.config.sections()}
        return _dict[section] if section in _dict else _dict

    def getConfig(self) -> configparser.ConfigParser:
        self.__updateConfig()
        return self.config

    def __updateConfig(self) -> None:
        _config = configparser.ConfigParser()
        _filename = self.config_file_name
        
        if len(_config) == 1 or not path.isfile(_filename): #File has not yet been loaded or has been deleted
            _config,_filename = self.__getConfigFromFiles()
        elif path.getmtime(_filename) != self.config_last_change_time: #File has been updated
            _config.clear()
            _config.read(_filename)
        else:
            # no changes
            return
        
        self.config_file_name = _filename
        self.config = _config
        self.config_last_change_time = path.getmtime(_filename)
        
        
    def __getConfigFromFiles(self):
        _config = configparser.ConfigParser()
        _filename = ""
        
        (_, _, filenames) = next(walk("."))
        
        # grabs first .ini file in root that has a token and is not template.ini
        for filename in filenames:
            if filename.endswith(".ini") and filename != "template.ini":
                _config.read(filename)
                if not self.__validateConfig(_config):
                    _config.clear()
                    continue
                _filename = filename
                break
            
        if len(_config) == 1 and path.isfile("template.ini"):
            _config.clear()
            _filename = "template.ini"
            _config.read("template.ini")
            if not self.__validateConfig(_config):
                _config.clear()
                _filename = ""
        if len(_config) == 1:     
            raise Exception("Failed to load any ini file")
            
        return _config, _filename
        
    def __validateConfig(self, config:configparser.ConfigParser):
        if config["DISCORD"]["bot_token"] == "<BOT_TOKEN>":
            print("Bot token is not set")
            return False
        if not config.has_section("DISCORD"):
            print("DISCORD Section missing in config file")
            return False
        if  not config.has_option("DISCORD","bot_token"):
            print("bot_token value missing in config file")
            return False
        if  not config.has_option("DISCORD","bot_command_prefix"):
            print("bot_command_prefix value missing in config file, using default of !")
            config.set(section="DISCORD", option="bot_command_prefix", value= "!")
            #return False
        return True
    
    

def getConfigLoader() -> IniParser:
    global _loaded_config
    if not _loaded_config:
        _loaded_config = IniParser()
    return _loaded_config

def getConfigAsDict(section:str = ""):
    return getConfigLoader().getConfigAsDict(section)

def getConfig():
    return getConfigLoader().getConfig()