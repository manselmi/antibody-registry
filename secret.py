# vim: set ft=python :


"""
Read secrets from various sources.

Pydantic Secret Types documentation:
https://docs.pydantic.dev/latest/usage/types/#secret-types
"""

import os
import shlex
import subprocess
from subprocess import PIPE
from typing import TYPE_CHECKING, TypedDict, Unpack

import structlog
from pydantic.types import SecretStr

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

LOGGER = structlog.get_logger(__name__)

Secret = SecretStr


class EnvLookupError(Exception):
    def __init__(self, name: str, /) -> None:
        super().__init__(f"environment variable name not found: {name}")


class _ReadTextKwargs(TypedDict, total=False):
    encoding: str | None
    errors: str | None
    newline: str | None


def secret_cmd_argv(argv: Sequence[str], /) -> Secret:
    """
    Read a secret from the given command's standard output.

    Example:
        >>> with structlog.testing.capture_logs():
        ...     secret = secret_cmd_argv(["/usr/bin/printf", "%s", "secret_value"])
        >>> print(secret.get_secret_value())
        secret_value
    """
    log = LOGGER.bind(secret_cmd_argv=argv)
    log.debug("run_secret_cmd")
    return Secret(
        subprocess.run(argv, check=True, encoding="utf-8", stdout=PIPE).stdout  # noqa:S603
    )


def secret_cmd_env_var(name: str, /) -> Secret:
    """
    Read a secret from the standard output of the command defined in the given environment variable.

    Example:
        >>> os.environ["SECRET_CMD"] = "/usr/bin/printf %s 'secret_value'"
        >>> with structlog.testing.capture_logs():
        ...     secret = secret_cmd_env_var("SECRET_CMD")
        >>> print(secret.get_secret_value())
        secret_value
    """
    log = LOGGER.bind(secret_cmd_env_var=name)
    log.debug("read_secret_cmd_env_var")
    try:
        value = os.environ[name]
    except KeyError as exc:
        log.exception("secret_cmd_env_var_is_unset")
        raise EnvLookupError(name) from exc
    argv = shlex.split(value)
    return secret_cmd_argv(argv)


def secret_env_var(name: str, /) -> Secret:
    """
    Read a secret from the given environment variable.

    Example:
        >>> os.environ["SECRET"] = "secret_value"
        >>> with structlog.testing.capture_logs():
        ...     secret = secret_env_var("SECRET")
        >>> print(secret.get_secret_value())
        secret_value
    """
    log = LOGGER.bind(secret_env_var=name)
    log.debug("read_secret_env_var")
    try:
        return Secret(os.environ[name])
    except KeyError as exc:
        log.exception("secret_env_var_is_unset")
        raise EnvLookupError(name) from exc


def secret_file(path: Path, /, **read_text_kwargs: Unpack[_ReadTextKwargs]) -> Secret:
    """
    Read a secret from the given path.

    Example:
        >>> from contextlib import redirect_stdout
        >>> from os import devnull
        >>> from tempfile import NamedTemporaryFile
        >>> encoding = "utf-8"
        >>> with NamedTemporaryFile(mode="w+t", encoding=encoding) as secret_fobj:
        ...     with open(devnull, mode="wt") as devnull_fobj, redirect_stdout(devnull_fobj):
        ...         secret_fobj.write("secret_value")
        ...     secret_fobj.flush()
        ...     with structlog.testing.capture_logs():
        ...         secret = secret_file(Path(secret_fobj.name), encoding=encoding)
        >>> print(secret.get_secret_value())
        secret_value
    """
    log = LOGGER.bind(secret_file=path)
    log.debug("read_secret_file")
    try:
        return Secret(path.read_text(**read_text_kwargs))
    except FileNotFoundError:
        log.exception("secret_file_not_found")
        raise
    except PermissionError:
        log.exception("secret_file_bad_perms")
        raise
