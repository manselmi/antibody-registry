# vim: set ft=python :

"""
Read a secret from a program's standard output.

Pydantic Secret Types documentation:
https://docs.pydantic.dev/latest/usage/types/#secret-types
"""

import os
import shlex
import subprocess
from collections.abc import Sequence
from subprocess import PIPE

import structlog
from pydantic.types import SecretStr

logger = structlog.get_logger(__name__)


Secret = SecretStr


class EnvLookupError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"environment variable name not found: {name}")


def secret_cmd_argv(argv: Sequence[str]) -> Secret:
    """
    Read a secret from the given program's standard output.

    Example:
        >>> with structlog.testing.capture_logs():
        ...     secret = secret_cmd_argv(["/usr/bin/printf", "%s", "secret_value"])
        >>> print(secret.get_secret_value())
        secret_value
    """
    log = logger.bind(secret_cmd_argv=argv)
    log.debug("run_secret_cmd")
    return Secret(
        subprocess.run(argv, check=True, encoding="utf-8", stdout=PIPE).stdout  # noqa:S603
    )


def secret_cmd_env_var(name: str) -> Secret:
    """
    Read a secret from the standard output of the program referenced by
    the given environment variable.

    Example:
        >>> os.environ["SECRET_CMD"] = "/usr/bin/printf %s 'secret_value'"
        >>> with structlog.testing.capture_logs():
        ...     secret = secret_cmd_env_var("SECRET_CMD")
        >>> print(secret.get_secret_value())
        secret_value
    """
    log = logger.bind(secret_cmd_env_var=name)
    log.debug("read_secret_cmd_env_var")
    try:
        value = os.environ[name]
    except KeyError as exc:
        log.exception("secret_cmd_env_var_is_unset")
        raise EnvLookupError(name) from exc
    argv = shlex.split(value)
    return secret_cmd_argv(argv)


def secret_env_var(name: str) -> Secret:
    """
    Read a secret from the given environment variable.

    Example:
        >>> os.environ["SECRET"] = "secret_value"
        >>> with structlog.testing.capture_logs():
        ...     secret = secret_env_var("SECRET")
        >>> print(secret.get_secret_value())
        secret_value
    """
    log = logger.bind(secret_env_var=name)
    log.debug("read_secret_env_var")
    try:
        return Secret(os.environ[name])
    except KeyError as exc:
        log.exception("secret_env_var_is_unset")
        raise EnvLookupError(name) from exc
