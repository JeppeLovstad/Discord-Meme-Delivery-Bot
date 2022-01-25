from types import ModuleType
from discord.ext import commands
import importlib  # reload, import_module
from os import path
import sys
import utils.iniparser as iniparser

_module_loader = None


def get_module_loader(bot):
    global _module_loader
    if not _module_loader:
        _module_loader = ModuleLoader(bot=bot)
    return _module_loader


class CogAlreadyRegistered(Exception):
    pass


class InvalidConfig(Exception):
    pass


class ModuleLoader:
    dict_cogname_info = {}  # cog_name: cog_info
    _bot: commands.Bot

    def __init__(self, bot: commands.Bot):
        self._bot = bot
        self.__update_cogs_info_from_dict(self.__get_cogs_info_dict_from_config())

    def load_cog(self, cog_name: str, force_reload: bool = False) -> str:
        cog_name = cog_name.lower()
        if self.is_cog_enabled(cog_name) and force_reload:
            self.unload_cog(cog_name)
        elif self.is_cog_enabled(cog_name) and not force_reload:
            raise CogAlreadyRegistered(
                "Cog is already loaded, set force_reload = 1 to reload"
            )

        cog = self.__get_instantiated_cog_from_cog_name(cog_name)
        if not isinstance(cog, str):
            self._bot.add_cog(cog)
            return f"Cog: {cog_name} loaded"
        return f"Cog: {cog_name} could not be loaded, {cog}"

    def unload_cog(self, cog_name) -> str:
        cog_name = cog_name.lower()
        cog_info = self.get_cog_info_from_name(cog_name)
        if cog_info and self.is_cog_enabled(cog_name):
            self._bot.remove_cog(cog_info["module"].capitalize())
            if not self.is_cog_enabled(cog_name):
                return f"Cog: {cog_name} removed"
            else:
                return f"Cog: {cog_name} not removed, something went wrong"
        return f"Cog: {cog_name} not loaded"

    def get_cog_info_from_name(self, cog_name: str) -> dict | None:
        return self.dict_cogname_info.get(cog_name.lower())

    def is_cog_enabled(self, cog_name: str) -> bool | None:
        return cog_name.capitalize() in self._bot.cogs

    ### Force reload all cogs, even if file hasnt changed
    def reload_all_cogs(self):
        self.__update_cogs_info_from_dict(self.__get_cogs_info_dict_from_config())
        msgs = self.load_cogs(list(self.dict_cogname_info.keys()))
        return "\n".join(msgs)

    def reload_cog(self, cog_name) -> str:
        self.unload_cog(cog_name)
        self.load_cog(cog_name)
        return f"{cog_name} reloaded"

    def reload_cogs(self, cogs: list[str]) -> str:
        str_list = []
        self.unload_cogs(cogs)
        self.load_cogs(cogs)
        for cog_name in cogs:
            str_list.append(f"{cog_name} reloaded")
        return "\n".join(str_list)

    def load_cogs(self, cogs: list[str]) -> list[str]:
        str_list = []
        for cog_name in cogs:
            str_list.append(self.load_cog(cog_name))
        return str_list

    def unload_cogs(self, cogs: list[str]) -> list[str]:
        str_list = []
        for cog_name in cogs:
            str_list.append(self.unload_cog(cog_name))
        return str_list

    def list_cogs(self, cog_name:str = ""):
        if cog_name:
            return self.dict_cogname_info.get(cog_name)
        else:
            return self.dict_cogname_info.items()

    ### Get files that has changed and try to reload them.
    def sync_changed_files(self):
        # self.__update_cogs_info_from_dict()
        new_dict_cogname_info = self.__get_cogs_info_dict_from_config()

        cogs_to_load = []
        cogs_to_unload = []
        msgs = []

        for module_name, old_cog_info in self.dict_cogname_info.items():
            if self.is_cog_enabled(module_name):
                ### File not in new config
                if module_name not in new_dict_cogname_info:
                    cogs_to_unload.append(module_name)
                    msgs.append(f"Removing {module_name}, removed from config")

        for module_name, new_cog_info in new_dict_cogname_info.items():
            old_cog_info = self.get_cog_info_from_name(module_name)
            ### if cog exists and has been loaded already
            if old_cog_info and self.is_cog_enabled(module_name):
                ### File has changed
                if old_cog_info["last_change_date"] != new_cog_info["last_change_date"]:
                    cogs_to_load.append(module_name)
                    msgs.append(f"Reloading {module_name} file has changed")

        print("cogs_to_unload", cogs_to_unload)
        print("cogs_to_load", cogs_to_load)

        self.unload_cogs(cogs_to_unload)
        self.reload_cogs(cogs_to_load)

        ### update dict
        self.dict_cogname_info = new_dict_cogname_info

        return "\n".join(msgs)

    def __update_cogs_info_from_dict(self, cogs_dict):
        self.dict_cogname_info = cogs_dict

    def __get_cogs_info_dict_from_config(self) -> dict:
        config = iniparser.getConfigAsDict()
        cog_dicts = {}
        for module, value in config["BOT_MODULES"].items():
            cog_info = {}
            if value.lower() == "true":
                cog_info = self.__get_cog_info_from_config(module, config)
                cog_dicts[module.lower()] = cog_info
        return cog_dicts

    def __get_cog_info_from_config(self, module, config) -> dict:
        if "BOT_MODULES" not in config:
            raise InvalidConfig("BOT_MODULES must be set in config")

        if module not in config["BOT_MODULES"]:
            raise InvalidConfig(
                f"{module} must be set in config and have a boolean value"
            )

        main_classname = (
            config["BOT_MODULES"][f"{module}_main"]
            if f"{module}_main" in config["BOT_MODULES"]
            else module.capitalize()
        )
        module_path = (
            config["BOT_MODULES"][f"{module}_path"]
            if f"{module}_path" in config["BOT_MODULES"]
            else f"BotModules.{module}"
        )
        module_config = config[module.upper()] if module.upper() in config else {}
        cog_info = {
            "module": module,
            "main_classname": main_classname,
            "module_path": module_path,
            "module_config": module_config,
            "last_change_date": self.__get_bot_module_mdate(
                module_path.replace(".", "/")
            ),
        }
        return cog_info

    def __get_instantiated_cog_from_cog_name(self, cog_name: str) -> object | str:
        cog_info = self.get_cog_info_from_name(cog_name)
        if cog_info is not None:
            cog = self.__get_instantiated_cog_from_cog_info(cog_info)
        else:
            return f"No such cog"

        return cog

    def __get_instantiated_cog_from_cog_info(self, cog_info: dict) -> object | str:
        error_message = instantiated_cog = None

        # expand the cog_info
        module, main_classname, module_path, module_config = (
            cog_info["module"],
            cog_info["main_classname"],
            cog_info["module_path"],
            cog_info["module_config"],
        )

        try:
            # get class from folder
            uninstantiated_cog = self.__get_cog_from_bot_module(
                module_path, main_classname
            )
            # initate class
            instantiated_cog = uninstantiated_cog(bot=self._bot, config=module_config)
            # update cog class name if another is specified
            instantiated_cog.__cog_name__ = module.capitalize()
        except ModuleNotFoundError as e:
            error_message = e.args[0]
        except AttributeError as e:
            error_message = e.args[0]
        except Exception as e:
            error_message = e.args[0]

        if not error_message and instantiated_cog:
            return instantiated_cog
        else:
            return error_message

    def __get_bot_module_mdate(self, module: str):
        file_path = f"{module.lower()}.py"
        try:
            return path.getmtime(file_path)
        except FileNotFoundError as e:
            return None

    def __get_cog_from_bot_module(self, module_name: str, package_name: str):
        _module = self.__get_bot_ModuleType(module_name, package_name)
        cog = getattr(_module, package_name)
        return cog

    def __get_bot_ModuleType(
        self, module_name: str, package_name: str
    ) -> ModuleType | None:

        _module_type = None

        if not self.__bot_module_already_imported(module_name):
            _module_type = self.__import_bot_module(module_name, package_name)
        else:
            _module_type = self.__reload_imported_bot_module(module_name)

        return _module_type

    def __import_bot_module(self, module_name: str, package_name: str) -> ModuleType:
        _module = importlib.import_module(name=module_name, package=package_name)
        return _module

    def __bot_module_already_imported(self, module_name: str) -> bool:
        return module_name in sys.modules

    def __reload_imported_bot_module(self, module_name):
        _curr_module = sys.modules[module_name]
        _new_module = importlib.reload(_curr_module)
        return _new_module


if __name__ == "__main__":
    bot = commands.Bot(command_prefix="!")
    m = get_module_loader(bot=bot)
    from time import time

    print(m.dict_cogname_info, sep="\n")
    print(bot.cogs)
    print(m.reload_all_cogs())
    # utime("BotModules/googler.py", (time(), time()))
    print(m.unload_cog("aimeme"))
    print()

    # print(m.load_cog("Googler"))
    # print(m.unload_cog("Googler"))
    # print(bot.cogs)
    # print(m.load_cog("Googler"))
    # print(m.unload_cog("Googler"))
    # print(m.load_cog("Googler"))

    print(bot.cogs)
    # print(bot.cogs, bot.commands)
    # print(m.dict_cogname_info["Googler"], sep="\n")
    # print(m.unload_cog("d"))
    # print(bot.cogs, bot.commands)
    # print(m.dict_cogname_info["Googler"], sep="\n")
