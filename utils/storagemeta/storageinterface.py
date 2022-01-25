import abc


class StorageMeta(abc.ABC):
    @abc.abstractmethod
    def setup_connection() -> None:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_connection() -> None:
        pass
