#!/usr/bin/env python
# vim: set ft=python :

import datetime
import getpass
import itertools
import lzma
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from threading import RLock
from typing import Annotated

import lxml.html
import stamina
import structlog
import typer
from httpx import (
    URL,
    Auth,
    Client,
    Cookies,
    HTTPError,
    HTTPStatusError,
    Request,
    Response,
    Timeout,
    codes,
)
from lxml.etree import _ElementUnicodeResult

from logging_config import configure_logging
from secret import Secret, secret_cmd_argv, secret_env_var

logger = structlog.get_logger(__name__)


HTTP2 = True
DEFAULT_TIMEOUT_DURATION = datetime.timedelta(seconds=10)
FETCH_TIMEOUT_DURATION = datetime.timedelta(seconds=30)
FETCH_ATTEMPTS = 10
PAGE_SIZE = 500

DEFAULT_TIMEOUT = Timeout(DEFAULT_TIMEOUT_DURATION.total_seconds())
FETCH_TIMEOUT = Timeout(FETCH_TIMEOUT_DURATION.total_seconds())


class AntibodyRegistryAuth(Auth):
    def __init__(self, client: Client, username: Secret, password: Secret) -> None:
        self._client = client
        self._username = username
        self._password = password
        self._cookies: Cookies | None = None
        self._lock = RLock()

    @property
    def username(self) -> Secret:
        return self._username

    @property
    def password(self) -> Secret:
        return self._password

    @property
    def cookies(self) -> Cookies | None:
        with self._lock:
            return self._cookies

    def _set_cookie_header(self, request: Request) -> None:
        with self._lock:
            if self._cookies is not None:
                self._cookies.set_cookie_header(request)

    def sync_auth_flow(self, request: Request) -> Generator[Request, Response]:
        with self._lock:
            self._set_cookie_header(request)
            response = yield request

            if response.status_code == codes.UNAUTHORIZED:
                self._cookies = login_to_antibody_registry(
                    self._client, self._username, self._password
                )
                self._set_cookie_header(request)
                yield request

    async def async_auth_flow(self, request: Request) -> AsyncGenerator[Request, Response]:  # type: ignore[override] # noqa: ARG002
        msg = "async_auth_flow_not_implemented"
        raise RuntimeError(msg)


def login_to_antibody_registry(client: Client, username: Secret, password: Secret) -> Cookies:
    response = client.get(URL("https://www.antibodyregistry.org/login"), follow_redirects=True)
    response.raise_for_status()

    cookies = response.cookies
    tree = lxml.html.fromstring(response.content)
    xpath: list[_ElementUnicodeResult] = tree.xpath('//form[@id="kc-form-login"]/@action')  # type: ignore[assignment]
    if not xpath:
        msg = "login_post_url_not_found"
        logger.error(msg)
        raise RuntimeError(msg)
    login_post_url = URL(str(xpath[0]))

    response = client.post(
        login_post_url,
        cookies=cookies,
        data={
            "username": username.get_secret_value(),
            "password": password.get_secret_value(),
            "rememberMe": "on",
            "credentialId": "",
        },
        follow_redirects=True,
    )
    response.raise_for_status()

    return response.history[1].cookies


def get_antibody_registry_credentials() -> tuple[Secret, Secret]:
    if getpass.getuser() in {
        "manselmi",
    }:
        username = secret_cmd_argv(
            [
                "op",
                "read",
                "--no-newline",
                "op://yksesvynnyj573ps3dagfglceu/de3yx4c5zeor7ztpbleisrkcvi/username",
            ],
        )
        password = secret_cmd_argv(
            [
                "op",
                "read",
                "--no-newline",
                "op://yksesvynnyj573ps3dagfglceu/de3yx4c5zeor7ztpbleisrkcvi/password",
            ],
        )
    else:
        username = secret_env_var("ANTIBODY_REGISTRY_USERNAME")
        password = secret_env_var("ANTIBODY_REGISTRY_PASSWORD")

    return username, password


def retry(exc: Exception) -> bool:
    if isinstance(exc, HTTPStatusError):
        return codes.is_server_error(exc.response.status_code)
    return isinstance(exc, HTTPError)


def main(
    logging_config: Annotated[
        Path, typer.Option(help="file from which the logging configuration will be read")
    ] = Path("logging_config.json"),
    output_dir: Annotated[
        Path, typer.Option(help="directory to which the response bodies will be written")
    ] = Path("output"),
) -> None:
    configure_logging(logging_config)

    base_url = URL("https://www.antibodyregistry.org/api/antibodies")
    params = {"size": PAGE_SIZE}

    log = logger.bind(base_url=base_url)

    username, password = get_antibody_registry_credentials()
    output_dir.mkdir(exist_ok=True, parents=True)

    with Client(http2=HTTP2, timeout=DEFAULT_TIMEOUT) as client:
        client.auth = AntibodyRegistryAuth(client, username, password)

        for page in itertools.count(start=1):
            params["page"] = page
            path = output_dir.joinpath(f"{page}.xz")

            log = log.bind(params=params, path=path)

            if path.exists():
                log.info("fetch_skip")
                continue

            log.info("fetch_begin")
            for attempt in stamina.retry_context(on=retry, attempts=FETCH_ATTEMPTS, timeout=None):
                with attempt:
                    response = client.get(base_url, params=params, timeout=FETCH_TIMEOUT)
                    response.raise_for_status()
            log.debug("fetch_end")

            log.info("write_begin")
            with lzma.open(path, mode="wb") as fobj:
                fobj.write(response.content)
            log.debug("write_end")


if __name__ == "__main__":
    typer.run(main)
