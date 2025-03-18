#!/usr/bin/env python
# vim: set ft=python :

import getpass
import os
from collections.abc import Generator
from pathlib import Path
from typing import Annotated

import lxml.html
import structlog
import typer
from httpx import (
    URL,
    Auth,
    Client,
    Cookies,
    Request,
    Response,
    Timeout,
    codes,
)

from logging_config import configure_logging
from secret import Secret, secret_cmd_argv

logger = structlog.get_logger(__name__)


HTTP2 = True
TIMEOUT = Timeout(10.0)  # seconds


class AntibodyRegistryAuth(Auth):
    def __init__(self, cookies: Cookies | None = None, /) -> None:
        self._cookies = cookies

    @property
    def cookies(self) -> Cookies | None:
        return self._cookies

    def auth_flow(self, request: Request) -> Generator[Request, Response]:
        self.set_cookie_header(request)
        response = yield request

        if response.status_code == codes.UNAUTHORIZED:
            self._cookies = login_to_antibody_registry()
            self.set_cookie_header(request)
            yield request

    def set_cookie_header(self, request: Request) -> None:
        if self._cookies is not None:
            self._cookies.set_cookie_header(request)


def login_to_antibody_registry() -> Cookies:
    username, password = get_antibody_registry_credentials()

    with Client(follow_redirects=True, http2=HTTP2, timeout=TIMEOUT) as client:
        response = client.get(URL("https://www.antibodyregistry.org/login"))
        response.raise_for_status()

        cookies = response.cookies
        tree = lxml.html.fromstring(response.content)
        login_post_url = URL(tree.xpath('//form[@id="kc-form-login"]/@action')[0])  # type: ignore[arg-type,index]

        response = client.post(
            login_post_url,
            cookies=cookies,
            data={
                "username": username.get_secret_value(),
                "password": password.get_secret_value(),
                "rememberMe": "on",
                "credentialId": "",
            },
        )
        response.raise_for_status()

        return response.history[1].cookies


def get_antibody_registry_credentials() -> tuple[Secret, Secret]:
    try:
        username = Secret(os.environ["ANTIBODY_REGISTRY_USERNAME"])
        password = Secret(os.environ["ANTIBODY_REGISTRY_PASSWORD"])
    except KeyError:
        if getpass.getuser() not in {"manselmi", "m.anselmi"}:
            raise
        username = secret_cmd_argv(
            [
                "op",
                "read",
                "--no-newline",
                "op://yksesvynnyj573ps3dagfglceu/ynqycbcmytlr3qx4ggbxioriiu/username",
            ],
        )
        password = secret_cmd_argv(
            [
                "op",
                "read",
                "--no-newline",
                "op://yksesvynnyj573ps3dagfglceu/ynqycbcmytlr3qx4ggbxioriiu/password",
            ],
        )

    return username, password


def main(
    logging_config: Annotated[
        Path, typer.Option(help="file from which a logging configuration will be read")
    ] = Path("logging_config.json"),
) -> None:
    configure_logging(logging_config)

    auth = AntibodyRegistryAuth()
    with Client(auth=auth, http2=HTTP2, timeout=TIMEOUT) as client:
        for url in map(
            URL,
            [
                "https://www.antibodyregistry.org/api/antibodies?size=10&page=51",
                "https://www.antibodyregistry.org/api/antibodies?size=10&page=52",
            ],
        ):
            client.get(url)


if __name__ == "__main__":
    typer.run(main)
