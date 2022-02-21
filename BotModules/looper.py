from discord.ext import commands, tasks
from collections import defaultdict


class Looper(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.bot = bot
        self.config = config
        # self.loops = {} # Loop = bool:enabled
        self.channels = defaultdict(dict)  # {channel: {loop: current_iteration:int}}
        self.max_loops_per_channel = 5
        self.looper.change_interval(minutes=1)
        self.looper.start()

    def cog_unload(self):
        self.looper.cancel()

    @commands.command()
    async def setloop(self, ctx, command: str, interval: int = 10, *parameters: str):
        loop = self.create_loop(
            ctx=ctx, command=command, parameters=list(parameters), interval=interval
        )

        msg = self.add_loop_to_channel(ctx.channel.id, loop)
        await ctx.send(msg)

    @commands.command()
    async def removeloop(self, ctx, command: str):
        success = self.remove_loop_from_channel(ctx.channel.id, command)
        await ctx.send("Removed loop" if success else "Could not find loop")

    @commands.command()
    async def listloops(self, ctx):
        msgs = self.get_loops_for_channel(ctx.channel.id)
        msgs = list(map(str, msgs))
        if msgs:
            await ctx.send("\n".join(msgs))
        else:
            await ctx.send("No loops, add some!")

    @commands.command()
    async def setloopstatus(self, ctx, command: str, status=""):
        loop = self.get_specific_loop_for_channel(ctx.channel.id, command)
        if not loop:
            await ctx.send("Could not find loop")
            return None

        if status.lower() in (
            "true",
            "1",
            "enable",
            "enabled",
            "start",
            "run",
            "ready",
        ):
            loop._is_enabled = True
            await ctx.send("loop enabled")
        else:
            loop._is_enabled = False
            await ctx.send("loop disabled")

    @tasks.loop()
    async def looper(self):
        loops = []

        if len(self.channels) == 0:
            return

        for loop_dict in self.channels.values():
            loops.append(list(loop_dict.values())[0])

        for loop in loops:
            if not loop:
                continue
            if self.looper.current_loop % loop._interval == 0:
                command, parameters = loop.get_execute_command()
                try:
                    await loop._ctx.invoke(self.bot.get_command(command), *parameters)
                except Exception as e:
                    print(f"loop {loop} disabled: it failed with exception {e}")
                    loop._is_enabled = False

    def create_loop(
        self, ctx, command: str, interval: int = 10, parameters: list[str] = []
    ):
        return Loop(
            ctx=ctx, command=command, parameters=list(parameters), interval=interval
        )

    def get_loops_for_channel(self, channel_id: int) -> list:
        return list(self.channels[channel_id].values())

    def get_specific_loop_for_channel(self, channel_id: int, command: str):
        loop_id = f"{channel_id}{command}"
        if loop_id not in self.channels[channel_id]:
            return None
        else:
            return self.channels[channel_id][loop_id]

    def add_loop_to_channel(self, channel_id: int, loop):
        command = self.bot.get_command(loop._command)

        if not isinstance(loop, Loop):
            return "Must supply a loop"

        if not command or command.hidden:
            return "command does not exist"

        if len(self.get_loops_for_channel(channel_id)) >= self.max_loops_per_channel:
            return f"Too many loops, remove another loop first"

        if channel_id not in self.channels:
            self.channels[channel_id] = {}

        msg = ""
        if loop.id in self.channels[channel_id]:
            msg = "Loop updated: "
        else:
            msg = "Loop added: "

        self.channels[channel_id][loop.id] = loop

        return msg + str(loop)

    def remove_loop_from_channel(self, channel_id: int, command):
        loop_id = f"{channel_id}{command}"
        if loop_id not in self.channels[channel_id]:
            return False
        else:
            del self.channels[channel_id][loop_id]
            return True


class Loop:
    def __init__(self, ctx, command: str, parameters: list[str], interval: int):
        self._ctx = ctx
        self._channel = ctx.channel
        self._channel_id = ctx.channel.id
        self._command = command
        self._parameters = parameters
        self._interval = interval
        self._is_enabled = True
        self.id = f"{self._channel_id}{self._command}"

    def get_execute_command(self):
        return self._command, tuple(self._parameters)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __bool__(self):
        return self._is_enabled

    def __str__(self):
        return f"command:{self._command}, parameters:{self._parameters}, interval:{self._interval} minutes, enabled:{self._is_enabled}"


if __name__ == "__main__":
    from configparser import ConfigParser

    config = ConfigParser()
    config.read("config.ini")
    bot = commands.Bot(command_prefix="!")
    m = Looper(bot=bot, config=config)
    ctx = type("", (object,), {"channel": 1})()
    l = m.create_loop(ctx, "help")
    l2 = m.create_loop(ctx, "help2")
    # print(isinstance(l, Loop))
    # print(m.add_loop_to_channel(1, l))
    # print(m.add_loop_to_channel(1, l2))
    # print(m.add_loop_to_channel(2, l))
    # loops = []
    # for loop_dict in m.channels.values():
    #     loops.append(list(loop_dict.values())[0])

    # print(loops[0]._interval)

    # print(m.add_loop_to_channel(1,"1test"))
    # print(set([loop for loop in list(m.channels.values())]))
    # print(bot.get_command("help").commands)
    # print(m.test_loop())
    # print(m.get_specific_loop_for_channel(1,"help"))
    # print(m.remove_loop_from_channel(1,"help"))
    # print(m.channels[1])
    # print(m.channels[1]["1test"])
