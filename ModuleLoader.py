from discord.ext import commands

_module_loader = None


def getModuleLoader(bot, config):
    global _module_loader
    if not _module_loader:
        _module_loader = ModuleLoader(bot=bot, config=config)
    return _module_loader


class ModuleLoader:
    cogs = {}
    _bot: commands.Bot

    def __init__(self, bot: commands.Bot, config):
        self._bot = bot

        cog_info = self.getCogInfoFromConfig(config)
        self.load_cogs(cog_info)

    def reload_cogs(self, cogs):
        pass

    def load_cogs(self, cogs):
        for cogInfo in cogs:
            cog = self.instantiateCog(cogInfo)
            if cog:
                self._bot.add_cog(cog)

    def unload_cog(self, cog_name):
        pass

    def getCogInfoFromConfig(self, config):
        cogs = []
        for module, enabled in config["BOT_MODULES"].items():
            if enabled == "True":

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
                }
                cogs.append(cog)
        return cogs

    def instantiateCog(self, cog):
        error_message = initiated_class = None
        module, main_classname, module_path, module_config = (
            cog["module"],
            cog["main_classname"],
            cog["module_path"],
            cog["module_config"],
        )
        try:
            # get class from folder
            imported_class = self.import_bot_module(module_path, main_classname)
            # check if module specific config exists

            try:
                # initate class
                initiated_class = imported_class(bot=self._bot, config=module_config)
                # update class name
                initiated_class.__cog_name__ = module.capitalize()
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
            return initiated_class
        else:
            print(error_message)

    def import_bot_module(self, module, name):
        module = __import__(module, fromlist=[name])
        return getattr(module, name)
