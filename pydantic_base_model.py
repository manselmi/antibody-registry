# vim: set ft=python :

from pydantic.config import ConfigDict
from pydantic.main import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        allow_inf_nan=False,
        extra="forbid",
        frozen=True,
        strict=True,
    )


class NoneError(ValueError):
    def __init__(self) -> None:
        super().__init__("value may not be None")


def validate_not_none[T](value: T) -> T:
    if value is None:
        raise NoneError
    return value
