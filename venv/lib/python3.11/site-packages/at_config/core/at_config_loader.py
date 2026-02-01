from typing import Any
from typing import Dict
from typing import Literal
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator
from pydantic import RootModel

from at_config.core.at_config_handler import ATComponentConfig
from at_config.core.at_config_item import ExecMethodConfigItem
from at_config.core.at_config_item import LocalFileConfigItem
from at_config.core.at_config_item import RawDataConfigItem
from at_config.core.context import Context


class RawDataItem(BaseModel):
    item_type: Literal["raw_data"] = Field(default="raw_data")
    data_: Any = Field(alias="data")

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def extract_data(cls, data: Any) -> Dict[str, Any]:
        if isinstance(data, dict):
            if "data" not in data:
                return {"data": data}
        else:
            return {"data": data}
        return data

    async def to_internal(self, context: Context = None, *, parameter: str) -> RawDataConfigItem:
        result = RawDataConfigItem(parameter, data=self.data_)
        await result.execute()
        return result


class LocalFileItem(BaseModel):
    item_type: Literal["local_file"] = Field(default="local_file")
    path: str

    model_config = ConfigDict(extra="ignore")

    async def to_internal(self, context: Context = None, *, parameter: str) -> LocalFileConfigItem:
        result = LocalFileConfigItem.build(parameter, path=self.path)
        await result.execute()
        return result


class ExecMethodItem(BaseModel):
    item_type: Literal["method"] = Field(default="method")
    component: str
    method: str
    method_args: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="ignore")

    async def to_internal(self, context: Context = None, *, parameter: str) -> ExecMethodConfigItem:
        result = ExecMethodConfigItem(
            parameter, component=self.component, method=self.method, method_args=self.method_args, context=context
        )
        await result.execute()
        return result


ConfigItem = Union[LocalFileItem, ExecMethodItem, RawDataItem]


class ComponentConfig(RootModel[Dict[str, ConfigItem]]):
    async def to_internal(self, context: Context = None) -> ATComponentConfig:
        return ATComponentConfig(
            {
                parameter: await item.to_internal(context=context, parameter=parameter)
                for parameter, item in self.root.items()
            }
        )


class AppConfig(RootModel[Dict[str, ComponentConfig]]):
    async def to_internal(self, context: Context = None) -> Dict[str, ATComponentConfig]:
        return {component: await config.to_internal(context=context) for component, config in self.root.items()}


async def load_config(data: dict, context: Context = None) -> Dict[str, ATComponentConfig]:
    return await AppConfig.model_validate(data).to_internal(context=context)


async def load_component_config(data: dict, context: Context = None) -> ATComponentConfig:
    return await ComponentConfig.model_validate(data).to_internal(context=context)
