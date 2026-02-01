from typing import Dict

from at_config.core.at_config_item import ATConfigItem


class ATComponentConfig:
    items: Dict[str, ATConfigItem]

    def __init__(self, items: Dict[str, ATConfigItem], *args, **kwargs) -> None:
        self.items = items

    @property
    def __dict__(self) -> dict:
        def exclude_parameter(item: ATConfigItem) -> dict:
            res = item.__dict__
            res.pop("parameter", None)
            return res

        return {item.parameter: exclude_parameter(item) for item in self.items.values()}
