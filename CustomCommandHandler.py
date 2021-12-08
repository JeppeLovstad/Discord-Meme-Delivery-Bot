from io import FileIO
import json
from itertools import combinations
import random


class CustomCommandHandler():
    command_dict = {}
    file_name = "commands.json"

    def addCommand(self, command: str, response: str) -> bool:
        try:
            self.command_dict.setdefault(command, set()).add(response)
            return True
        except Exception as e:
            print(e)
            return False

    def deleteCommand(self, command: str) -> bool:
        try:
            if command in self.command_dict:
                self.command_dict.pop(command)
                return True
            return False
        except:
            return False

    def getResponseToMessage(self, message: str) -> str:
        commands = message.split()
        commands_expanded = []
        for i, j in combinations(range(len(commands) + 1), 2):
            commands_expanded.append(" ".join(commands[i:j]))
        valid_commands = list(filter(lambda x: x is not None, map(
            self.getResponseToCommand, commands_expanded)))
        # print(valid_commands)
        # print(commands_expanded)
        if valid_commands:
            return '\n'.join(valid_commands)
        else:
            return None

    def getResponseToCommand(self, command: str) -> str:

        try:
            if command in self.command_dict:
                commands = list(self.command_dict[command])
            else:
                return None
        except:
            return None
        return random.choice(commands)  # '\n'.join([f"{v}" for v in commands])

    def updateFile(self) -> bool:
        try:
            intermediateDict = {k: list(v)
                                for k, v in self.command_dict.items()}
            with open(self.file_name, "w") as outfile:
                json.dump(intermediateDict, outfile)
            return True
        except Exception as e:
            print(e)
            return False

    def __init__(self) -> None:
        try:
            with open(self.file_name) as infile:
                self.command_dict = {k: set(v) for k, v in json.load(infile)}
        except FileNotFoundError:
            pass
        # file broken use empty
        except Exception:
            pass

    # Cannot call open in del
    # def __exit__(self):
    #     print("saving file")
    #     with open(self.file_name, "w") as outfile:
    #         json.dump(self.command_dict, outfile)


# c = CustomCommandHandler()
# print(c.addCommand("test", "wow much so"))
# print(c.addCommand("test", "wow much too"))
# print(c.deleteCommand("test"))
# print(c.addCommand("i am", "wow much too"))
# print(c.addCommand("i am", "wow much too test"))
# print(c.getResponseToMessage("i am test this"))
# print(c.updateFile())
