# vim: set ft=python :

import logging.config
import sys
from collections.abc import Mapping, Sequence
from enum import StrEnum, auto
from types import TracebackType
from typing import Any

import orjson
import structlog
from pydantic.fields import Field
from structlog.typing import Processor

from pydantic_base_model import BaseModel as Model

HANDLER_NAME = "default"
LOGGER = structlog.get_logger(__name__)
STREAM = sys.stdout


class Formatter(StrEnum):
    AUTO = auto()
    PRETTY = auto()
    JSON = auto()


class LevelName(StrEnum):
    NOTSET = auto()
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class HandlerConfig(Model):
    formatter: Formatter = Field(...)


class LoggerConfig(Model):
    level: LevelName = Field(...)


type LoggersConfig = Mapping[str, LoggerConfig]


class LoggingConfig(Model):
    handler: HandlerConfig = Field(...)
    loggers: LoggersConfig = Field(...)


def configure_logging(
    config: LoggingConfig,
    /,
    *,
    processors: Sequence[Processor] | None = None,
) -> None:
    if (formatter := config.handler.formatter) == Formatter.AUTO:
        formatter = Formatter.PRETTY if STREAM.isatty() else Formatter.JSON

    default_stdlib_loggers_config = to_stdlib_loggers_config(
        {__name__: LoggerConfig(level=LevelName.CRITICAL)}
    )
    stdlib_loggers_config = to_stdlib_loggers_config(config.loggers)

    shared_processors: list[Processor] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "incremental": False,
            "formatters": {
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "foreign_pre_chain": shared_processors,
                    "processors": [
                        structlog.processors.dict_tracebacks,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.processors.JSONRenderer(serializer=orjson.dumps),
                    ],
                },
                "pretty": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "foreign_pre_chain": shared_processors,
                    "processors": [
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.dev.ConsoleRenderer(),
                    ],
                },
            },
            "handlers": {
                HANDLER_NAME: {
                    "class": "logging.StreamHandler",
                    "formatter": formatter,
                    "level": LevelName.NOTSET.upper(),
                    "stream": STREAM,
                },
            },
            "loggers": {
                **default_stdlib_loggers_config,
                **stdlib_loggers_config,
            },
        }
    )

    structlog.configure(
        cache_logger_on_first_use=True,
        logger_factory=structlog.stdlib.LoggerFactory(),
        processors=[
            structlog.contextvars.merge_contextvars,
            *shared_processors,
            *(processors or []),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
    )

    sys.excepthook = handle_unhandled_exception


def handle_unhandled_exception(
    type_: type[BaseException],
    value: BaseException,
    traceback: TracebackType | None,
    /,
) -> None:
    if issubclass(type_, Exception):
        LOGGER.critical("unhandled_exception", exc_info=(type_, value, traceback))
    sys.__excepthook__(type_, value, traceback)


def to_stdlib_loggers_config(loggers_config: LoggersConfig, /) -> Mapping[str, Mapping[str, Any]]:
    return {
        k: {"handlers": [HANDLER_NAME], "level": v.level.upper()} for k, v in loggers_config.items()
    }
