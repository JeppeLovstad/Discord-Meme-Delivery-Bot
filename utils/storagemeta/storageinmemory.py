from abc import ABCMeta
from storageinterface import StorageMeta
import json
import utils.iniparser as iniparser


class StorageInMemory(StorageMeta, metaclass=ABCMeta):

    messages_dict = dict()
    key_values_dict = dict()

    def __init__(self):
        pass

    async def __aenter__(self):
        return self

    async def __setup_storage_method__(self, postgres_args) -> None:
        pass

    def store(
        self,
        key: tuple[str, ...],
        value: object,
        module: str,
        server: str = "",
        channel: str = "",
        user: str = "",
        value_type: str = "str",
    ) -> bool:

        if value_type == "json":
            value = json.dumps(value)

        dict_key = (key, module, server, channel, user)
        self.key_values_dict[dict_key] = (value, value_type)

        return True

    def retrieve(
        self,
        key: tuple[str, ...],
        module: str,
        server: str = "",
        channel: str = "",
        user: str = "",
    ) -> object:

        dict_key = (key, module, server, channel, user)
        return_val = self.key_values_dict.get(dict_key, None)

        if return_val is not None and return_val[1] == "json":
            return_val = json.loads(return_val[0])
        elif return_val is not None:
            return_val = return_val[0]

        return return_val if return_val else None

    def delete(
        self,
        key: tuple[str, ...],
        module: str,
        server: str = "",
        channel: str = "",
        user: str = "",
    ) -> bool:

        dict_key = (key, module, server, channel, user)
        return True

    def store_message(
        self,
        key: tuple[str, ...],
        value: str,
        module: str,
        server: str = "",
        channel: str = "",
        user: str = "",
    ) -> bool:
        return True

    def retrieve_message(
        self,
        message_id: int,
        server: str = "",
        channel: str = "",
        user: str = "",
        limit: int = 10,
    ) -> str:
        return ""

    def get_server(self, server_id: int):
        pass

    def get_channel(self, channel_id: int):
        pass

    def get_user(self, user_id: int):
        pass

    async def __aexit__(self, *args):
        pass


if __name__ == "__main__":
    dal = StorageInMemory()

    obj = {"Id": 78912, "Customer": "Jason Sweet", "Quantity": 1, "Price": 18.00}

    dal.store(
        key=("test", "2"),
        value=obj,
        module="meme",
        server="Gæve Gutter",
        channel="#trash",
        user="jeppe",
        value_type="str",
    )
    value = dal.retrieve(("test", "2"), "meme", "Gæve Gutter", "#trash", "jeppe")
    print(value)
