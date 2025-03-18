# vim: set ft=python :

import logging
import logging.config
import sys
from enum import StrEnum, auto
from pathlib import Path
from types import TracebackType

import orjson
import structlog
from pydantic.fields import Field
from structlog.typing import Processor

from pydantic_base_model import BaseModel as Model

logger = structlog.get_logger(__name__)


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


_Loggers = dict[str, LoggerConfig]


class LoggingConfig(Model):
    handler: HandlerConfig = Field(...)
    loggers: _Loggers = Field(...)


def configure_logging(path: Path) -> None:
    logging_config = load_logging_config(path)

    handler = "default"
    stream = sys.stdout

    if (formatter := logging_config.handler.formatter) == Formatter.AUTO:
        formatter = Formatter.PRETTY if stream.isatty() else Formatter.JSON

    def to_logger_configs(loggers: _Loggers):  # type: ignore[no-untyped-def]
        return {k: {"handlers": [handler], "level": v.level.upper()} for k, v in loggers.items()}

    default_logger_configs = to_logger_configs({__name__: LoggerConfig(level=LevelName.CRITICAL)})
    logger_configs = to_logger_configs(logging_config.loggers)

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    shared_processors: list[Processor] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
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
                handler: {
                    "class": "logging.StreamHandler",
                    "formatter": formatter,
                    "level": LevelName.NOTSET.upper(),
                    "stream": stream,
                },
            },
            "loggers": {
                **default_logger_configs,
                **logger_configs,
            },
        }
    )

    structlog.configure_once(
        cache_logger_on_first_use=True,
        logger_factory=structlog.stdlib.LoggerFactory(),
        processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        wrapper_class=structlog.stdlib.BoundLogger,
    )

    sys.excepthook = handle_unhandled_exception


def load_logging_config(path: Path) -> LoggingConfig:
    config = path.read_bytes()
    return LoggingConfig.model_validate_json(config)


def handle_unhandled_exception(
    type_: type[BaseException],
    value: BaseException,
    traceback: TracebackType | None,
    /,
) -> None:
    if issubclass(type_, Exception):
        logger.critical("unhandled_exception", exc_info=(type_, value, traceback))
    sys.__excepthook__(type_, value, traceback)
