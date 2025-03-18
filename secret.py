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
        >>> secret = secret_cmd_argv(["/usr/bin/printf", "%s", "secret_value"])
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
        >>> print(os.environ["SECRET_CMD"])
        /usr/bin/printf %s 'secret_value'
        >>> secret = secret_cmd_env_var("SECRET_CMD")
        >>> print(secret.get_secret_value())
        secret_value
    """
    log = logger.bind(secret_cmd_env_var=name)
    log.debug("read_secret_cmd_env_var")
    if (value := os.environ.get(name)) is None:
        log.error("secret_cmd_env_var_is_unset")
        raise EnvLookupError(name)
    argv = shlex.split(value)
    return secret_cmd_argv(argv)
