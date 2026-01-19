#!/usr/bin/env python
# vim: set ft=python :

import getpass
import itertools
import lzma
import sys
import time
from pathlib import Path
from threading import RLock
from typing import TYPE_CHECKING, Annotated

import lxml.html
import stamina
import structlog
import typer
from httpx import URL, Auth, Client, HTTPError, HTTPStatusError, Timeout, codes

from logging_config import LoggingConfig, configure_logging
from secret import secret_cmd_argv, secret_env_var

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from httpx import Cookies, Request, Response
    from lxml.etree import _ElementUnicodeResult

    from secret import Secret

LOGGER = structlog.get_logger(__name__)


BASE_URL = URL("https://www.antibodyregistry.org/api/antibodies")
HTTP2 = True
DEFAULT_TIMEOUT = Timeout(5)  # seconds
FETCH_TIMEOUT = Timeout(**{**DEFAULT_TIMEOUT.as_dict(), "read": 30})  # seconds
FETCH_ATTEMPTS = 3
PAGE_SIZE = 500


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


class XMLError(Exception):
    pass


def login_to_antibody_registry(client: Client, username: Secret, password: Secret) -> Cookies:
    response = client.get(URL("https://www.antibodyregistry.org/login"), follow_redirects=True)
    response.raise_for_status()

    cookies = response.cookies
    tree = lxml.html.fromstring(response.content)
    xpath: list[_ElementUnicodeResult] = tree.xpath('//form[@id="kc-form-login"]/@action')  # type: ignore[assignment]
    if not xpath:
        msg = "login_post_url_not_found"
        LOGGER.error(msg)
        raise XMLError(msg)
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
        status_code = exc.response.status_code
        return status_code == codes.TOO_MANY_REQUESTS or codes.is_server_error(status_code)
    return isinstance(exc, HTTPError)


def main(
    logging_config: Annotated[
        Path, typer.Option(help="file from which the logging configuration will be read")
    ] = Path("logging_config.json"),
    output_dir: Annotated[
        Path, typer.Option(help="directory to which the response bodies will be written")
    ] = Path("output"),
) -> None:
    configure_logging(LoggingConfig.model_validate_json(logging_config.read_bytes()))

    log = LOGGER.bind(base_url=str(BASE_URL))

    params = {"size": PAGE_SIZE}
    username, password = get_antibody_registry_credentials()
    output_dir.mkdir(exist_ok=True, parents=True)
    fetch_error = False

    with Client(http2=HTTP2, timeout=DEFAULT_TIMEOUT) as client:
        client.auth = AntibodyRegistryAuth(client, username, password)

        for page in itertools.count(start=1):
            params["page"] = page
            log = log.bind(params=params)

            path = output_dir.joinpath(f"{page}.xz")
            if path.exists():
                log = log.bind(path=str(path))
                log.info("fetch_skip")
                log = log.unbind("path")
                continue

            log.info("fetch_begin")
            try:
                for attempt in stamina.retry_context(
                    on=retry, attempts=FETCH_ATTEMPTS, timeout=None
                ):
                    with attempt:
                        response = client.get(BASE_URL, params=params, timeout=FETCH_TIMEOUT)
                        log = log.bind(status_code=response.status_code)

                        if response.status_code == codes.TOO_MANY_REQUESTS and (
                            retry_after := response.headers.get("retry-after")
                        ):
                            next_wait_seconds = attempt.next_wait
                            log = log.bind(
                                next_wait_seconds=next_wait_seconds, retry_after=retry_after
                            )
                            retry_after_seconds = int(retry_after)
                            sleep_seconds = max(retry_after_seconds - next_wait_seconds, 0)
                            log = log.bind(
                                retry_after_seconds=retry_after_seconds, sleep_seconds=sleep_seconds
                            )
                            log.warning("fetch_retry_after")
                            time.sleep(sleep_seconds)

                        response.raise_for_status()
            except Exception as exc:
                log.exception("fetch_error")
                fetch_error = True
                if isinstance(exc, HTTPError):
                    continue
                raise
            else:
                current_element = PAGE_SIZE * page
                total_elements = response.json()["totalElements"]
                log = log.bind(current_element=current_element, total_elements=total_elements)
                log.info("fetch_end")
                if current_element >= total_elements + PAGE_SIZE:
                    log.info("fetch_out_of_bounds")
                    break
            finally:
                log = log.try_unbind(
                    "current_element",
                    "next_wait_seconds",
                    "retry_after",
                    "retry_after_seconds",
                    "sleep_seconds",
                    "status_code",
                    "total_elements",
                )

            log = log.bind(path=path)
            log.info("write_begin")
            try:
                with lzma.open(path, mode="wb") as fobj:
                    fobj.write(response.content)
            except Exception, KeyboardInterrupt:
                log.exception("write_error")
                path.unlink(missing_ok=True)
                raise
            else:
                log.info("write_end")
            finally:
                log = log.unbind("path")

    if fetch_error:
        sys.exit(1)


if __name__ == "__main__":
    typer.run(main)
