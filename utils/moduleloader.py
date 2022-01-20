from discord.ext import commands
from discord.ext.commands import cog
import utils.iniparser as iniparser

_module_loader = None


def getModuleLoader(bot):
    global _module_loader
    if not _module_loader:
        _module_loader = ModuleLoader(bot=bot)
    return _module_loader


class ModuleLoader:
    dict_cogname_info = {}  # cog_name: cog_info
    _bot: commands.Bot

    def __init__(self, bot: commands.Bot):
        self._bot = bot
        self.__update_cog_info_from_config()

    def is_cog_enabled(self, cog_name):
        return self.dict_cogname_info[cog_name]["enabled"]

    def load_cog(self, cog_name: str, force_reload=False):
        if self.is_cog_enabled and force_reload:
            self.unload_cog(cog_name)
        else:
            return "Cog is already loaded set force_reload = 1 to reload"

        cog = self.__get_instantiated_cog_from_cog_name(cog_name)
        if cog:
            self._bot.add_cog(cog)

    def unload_cog(self, cog_name):
        if cog_name in self.dict_cogname_info:
            self._bot.remove_cog(cog_name)
            self.dict_cogname_info[cog_name]["enabled"] = False
            return f"Cog {cog_name} removed"
        else:
            return f"Could not remove {cog_name}, either it does not exist or something went wrong"

    def reload_all_cogs(self):
        self.__update_cog_info_from_config()
        self.load_cogs(self.dict_cogname_info)

    def reload_cog(self, cog_name):
        self.unload_cog(cog_name)
        self.load_cog(cog_name)

    def load_cogs(self, cogs: dict):
        for cog_name in list(cogs.keys()):
            self.load_cog(cog_name)

    def sync_bot_with_config(self):
        pass

    def __update_cog_info_from_config(self) -> None:
        config = iniparser.getConfigAsDict()
        for module, value in config["BOT_MODULES"].items():
            cog = {}
            if value.lower() == "true":
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
                module_config = (
                    config[module.upper()] if module.upper() in config else {}
                )
                cog = {
                    "module": module,
                    "main_classname": main_classname,
                    "module_path": module_path,
                    "module_config": module_config,
                    "enabled": False,
                }
                self.dict_cogname_info[main_classname] = cog

    def __get_cog_info_from_name(self, cog_name):
        return (
            self.dict_cogname_info[cog_name]
            if cog_name in self.dict_cogname_info
            else None
        )

    def __get_instantiated_cog_from_cog_name(self, cog_name: str):
        cog_info = self.__get_cog_info_from_name(cog_name)
        return self.__get_instantiated_cog_from_cog_info(cog_info)

    def __get_instantiated_cog_from_cog_info(self, cog_info):
        error_message = instantiated_cog = None

        module, main_classname, module_path, module_config = (
            cog_info["module"],
            cog_info["main_classname"],
            cog_info["module_path"],
            cog_info["module_config"],
        )
        try:
            # get class from folder
            imported_class = self.__import_bot_module(module_path, main_classname)
            # check if module specific config exists
            # initate class
            instantiated_cog = imported_class(bot=self._bot, config=module_config)
            # update cog class name if another is specified
            instantiated_cog.__cog_name__ = module.capitalize()
        except ModuleNotFoundError as e:
            print(f"no module found in {module_path}")
            error_message = e
        except AttributeError as e:
            print(f"no class '{main_classname}', found in module {module_path}")
            error_message = e
        except Exception as e:
            print(f"Could not instantiate {module} skipping..., \n Error: {e}")
            error_message = e

        if not error_message:
            cog_info["enabled"] = True
            return instantiated_cog
        else:
            print(error_message)
            return None

    def __import_bot_module(self, module, name):
        module = __import__(module, fromlist=[name])
        return getattr(module, name)


if __name__ == "__main__":
    bot = commands.Bot(command_prefix="!")
    m = getModuleLoader(bot=bot)

    print(m.dict_cogname_info["Googler"], sep="\n")
    print(bot.cogs)
    m.load_cog("Googler")
    print(bot.cogs, bot.commands)
    print(m.dict_cogname_info["Googler"], sep="\n")
    m.unload_cog("Googler")
    print(bot.cogs, bot.commands)
    print(m.dict_cogname_info["Googler"], sep="\n")
