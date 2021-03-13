""" Storing user data (email, mac-address) and
handling data storage (with pickle) """

import os
import pickle

from typing import Optional

from click_logging import ClickLogger


class StorageError(Exception):
    def __init__(self, status: int):
        super().__init__(f"http-status-code: {status}")
        self.status = int(status)


class Storage(object):
    def __init__(self, storage: str, log_level: str = 'warning'):
        self.storage = storage
        self.log = ClickLogger(log_level, 'Storage')

    def add(self, group: str, label: str, data: bytes) -> None:
        self.log.debug(f"add: {group=}, {label=}, {data=}")

        assert isinstance(group, str), "group have to be a string"
        assert isinstance(label, str), "label have to be a string"
        assert isinstance(data, bytes), "only bytes accepted for data"

        storage: str = self.storage
        group_path: list[str, bool] = [f"{self.storage}/{group}", False]
        label_path: str = f"{self.storage}/{group}/{label}"

        if group not in os.listdir(storage):
            self.log.debug(f"add: create group directory '{group_path[0]}'")
            os.makedirs(group_path[0])
            group_path[1] = True

        try:
            self.log.debug(f"add: write data to label '{label}'")

            with open(label_path, 'wb') as file:
                pickle.dump(data, file)

        except Exception as ex:
            self.log.error(f"write to {label_path} failed: '{ex}'")

            if group_path[1]:
                if os.exists(label_path):
                    os.remove(label_path)

                os.remove(group_path[0])

            raise StorageError(500)

    def get(self, group: str, label: str) -> bytes:
        self.log.debug(f"get: {group=}, {label=}")

        assert isinstance(group, str), "group have to be a string"
        assert isinstance(label, str), "label have to be a string"

        label_path = f"{self.storage}/{group}/{label}"

        if os.path.isfile(label_path):
            with open(label_path, 'rb') as file:
                return pickle.load(file)
        else:
            raise StorageError(404)  # label not exists in group

    def groups(self) -> list[str]:
        self.log.debug("groups: list groups in storage")

        return list(os.listdir(self.storage))

    def labels(self, group: str) -> list[str]:
        self.log.debug(f"labels: {group=}")

        assert isinstance(group, str), "group have to be a string"

        if group not in os.listdir(self.storage):
            raise StorageError(404)  # NOTE: group not exist

        return list(os.listdir(f"{self.storage}/{group}"))

    def remove(self, group: str, label: Optional[str] = None) -> None:
        self.log.debug(f"remove: {group=}, {label=}")

        assert isinstance(group, str), "group have to be a string"
        path = f"{self.storage}/{group}"

        if label is not None:
            assert isinstance(label, str), "label have to be a string"
            path = f"{self.storage}/{group}/{label}"

        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            for file in os.listdir(path):
                _path = f"{path}/{file}"
                if not os.path.isfile(_path):
                    self.log.critical(f"StorageError: path is not a file: {_path}")
                    raise StorageError(500)
                os.remove(_path)

            os.removedirs(path)
        else:
            raise StorageError(404)

    def rename(self, old: str, new: str) -> None:
        self.log.debug(f"rename_group: {old=}, {new=}")

        assert isinstance(old, str), "string expected for parameter 'old'"
        assert isinstance(new, str), "string expected for parameter 'new'"

        src = f"{self.storage}/{old}"
        dst = f"{self.storage}/{new}"

        if os.path.isdir(src):
            os.rename(src, dst)
        else:
            raise StorageError(404)
