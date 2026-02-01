import io
import json
import os
from typing import Any
from typing import Union
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import fromstring

import yaml

from at_config.core.context import Context


class ATConfigItem:
    parameter: str
    data: Union[dict, str, Element]

    def __init__(self, parameter: str, *args, **kwargs) -> None:
        self.parameter = parameter

    @property
    def item_type(self):
        return "abstract"

    @property
    def __dict__(self):
        return {"parameter": self.parameter, "item_type": self.item_type}

    async def execute(self, auth_token: str = None):
        pass


class RawDataConfigItem(ATConfigItem):
    data: dict

    def __init__(self, parameter: str, data: dict, *args, **kwargs) -> None:
        super().__init__(parameter, *args, **kwargs)
        self.data = data

    @property
    def item_type(self):
        return "raw_data"

    @property
    def __dict__(self):
        return {"data": self.data, **super().__dict__}


class FileConfigItem(ATConfigItem):
    @property
    def item_type(self):
        return "file"

    def get_readable(self, mode: str = "rb") -> io.TextIOBase:
        raise NotImplementedError()

    @property
    def content(self) -> bytes:
        return self.get_readable("rb").read()


class LocalFileConfigItem(FileConfigItem):
    path: str

    def __init__(self, parameter: str, path: str, *args, **kwargs) -> None:
        super().__init__(parameter, *args, **kwargs)
        self.path = path

    @property
    def item_type(self):
        return "local_file"

    def get_readable(self, mode: str = "rb") -> io.TextIOBase:
        return open(self.path, mode)

    @property
    def __dict__(self):
        return {"path": self.path, **super().__dict__}

    @property
    def ext(self) -> str:
        return os.path.splitext(self.path)[-1]

    @staticmethod
    def build(parameter: str, path: str, *args, **kwargs) -> "LocalFileConfigItem":
        try:
            ext_to_class = {".json": JSONFileItem, ".yaml": YAMLFileItem, ".yml": YAMLFileItem, ".xml": XMLFileItem}
            file_ext = os.path.splitext(path)[-1]
            if file_ext in ext_to_class:
                result = ext_to_class[file_ext](parameter, path, *args, **kwargs)
                result.data
                return result
        except Exception:
            return RawFileItem(parameter, path, *args, **kwargs)
        return RawFileItem(parameter, path, *args, **kwargs)


class JSONFileItemMixin:
    @property
    def data(self) -> dict:
        return json.load(self.get_readable())


class YAMLFileItemMixin:
    @property
    def data(self) -> dict:
        return yaml.safe_load(self.get_readable())


class XMLFileItemMixin:
    @property
    def data(self) -> Element:
        return fromstring(self.get_readable().read())


class RawFileItemMixin:
    @property
    def data(self) -> str:
        return self.content.decode()


class JSONFileItem(LocalFileConfigItem, JSONFileItemMixin):
    pass


class YAMLFileItem(LocalFileConfigItem, YAMLFileItemMixin):
    pass


class XMLFileItem(LocalFileConfigItem, XMLFileItemMixin):
    pass


class RawFileItem(LocalFileConfigItem, RawFileItemMixin):
    pass


class ExecMethodConfigItem(ATConfigItem):
    component: str
    method: str
    method_args: dict
    context: Union[Context, None]
    _data: Any

    def __init__(
        self, parameter, component: str, method: str, method_args: dict = None, context: Context = None, *args, **kwargs
    ):
        super().__init__(parameter, *args, **kwargs)
        self.component = component
        self.method = method
        self.method_args = method_args or {}
        self.context = context

    @property
    def item_type(self):
        return "method"

    @property
    def __dict__(self):
        return {"component": self.component, "method": self.method, "method_args": self.method_args, **super().__dict__}

    async def execute(self, auth_token: str = None) -> dict:
        if self.context is not None:
            if await self.context.component.check_external_registered(self.component):
                self._data = self.context.component.exec_external_method(
                    self.component, self.method, self.method_args, auth_token=auth_token or self.context.auth_token
                )

    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            raise RuntimeError(
                "Data not fetched yet. Please call execute() " "method first with fullfiled context of config."
            )
