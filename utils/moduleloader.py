from discord.ext import commands
from discord.ext.commands import cog
import utils.iniparser as iniparser

_module_loader = None

def getModuleLoader(bot, config):
    global _module_loader
    if not _module_loader:
        _module_loader = ModuleLoader(bot=bot)
    return _module_loader


class ModuleLoader:
    cogs = {} # name: (cog, cog_info, added_to_bot)
    _bot: commands.Bot

    def __init__(self, bot: commands.Bot):
        self._bot = bot
        cog_info = self.getCogInfoFromConfig()
        self.load_cogs(cog_info)

    def reload_cogs(self, cogs):
        pass

    def load_cogs(self, cogs):
        for cogInfo in cogs.values():
            cog = self.instantiateCogFromCogInfo(cogInfo[1])
            if cog:
                self._bot.add_cog(cog)

    def unload_cog(self, cog_name):
        if cog_name in self.cogs:
            self._bot.remove_cog(cog_name)
            return f"Cog {cog_name} removed"
        else:
            return f"Could not remove {cog_name}, either it does not exist or something went wrong"

    def getCogInfoFromConfig(self):
        config = iniparser.getConfigAsDict()
        cogs = []
        for module, enabled in config["BOT_MODULES"].items():
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
                    "enabled":enabled,
                }
                cogs.append(cog)
        return cogs

    def instantiateCogFromCogInfo(self, cog_info):
        error_message = instantiated_cog = None
        module, main_classname, module_path, module_config = (
            cog_info["module"],
            cog_info["main_classname"],
            cog_info["module_path"],
            cog_info["module_config"]
        )
        try:
            # get class from folder
            imported_class = self.import_bot_module(module_path, main_classname)
            # check if module specific config exists

            try:
                # initate class
                instantiated_cog = imported_class(bot=self._bot, config=module_config)
                # update class name
                instantiated_cog.__cog_name__ = module.capitalize()
            except Exception as e:
                print(f"Could not instantiate {module} skipping..., \n Error: {e}")
                error_message = e
        except ModuleNotFoundError as e:
            print(f"no module found in {module_path}")
            error_message = e
        except AttributeError as e:
            print(f"no class '{main_classname}', found in module {module_path}")
            error_message = e

        if not error_message:
            return instantiated_cog
        else:
            print(error_message)

    def import_bot_module(self, module, name):
        module = __import__(module, fromlist=[name])
        return getattr(module, name)
