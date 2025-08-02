<!-- vim: set ft=markdown : -->


# Antibody Registry downloader

## Summary

The script `download.py` demonstrates automated headless login to the Antibody Registry
with [`httpx`](https://www.python-httpx.org/) by implementing a [custom authentication
scheme](https://www.python-httpx.org/advanced/authentication/#custom-authentication-schemes).

## Prerequisites

### Required

* [Pixi](https://pixi.sh)

* Antibody Registry username and password in the environment variables `ANTIBODY_REGISTRY_USERNAME`
  and `ANTIBODY_REGISTRY_PASSWORD`, respectively.

### Optional

* Configure Git hooks:

    ``` shell
    pixi run -- pre-commit-install
    ```

## Example

### Invocation

``` shell
pixi run -- ./download.py
```

### Output

``` text
2025-08-02T04:21:17.185231Z [info     ] fetch_begin                    [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 1} path=PosixPath('output/1.xz')
2025-08-02T04:21:19.205919Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/api/antibodies?size=500&page=1 "HTTP/2 200 OK" [httpx]
2025-08-02T04:21:19.406552Z [info     ] write_begin                    [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 1} path=PosixPath('output/1.xz')
2025-08-02T04:21:19.465958Z [info     ] fetch_begin                    [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 2} path=PosixPath('output/2.xz')
2025-08-02T04:21:19.513076Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/api/antibodies?size=500&page=2 "HTTP/2 401 Unauthorized" [httpx]
2025-08-02T04:21:19.553050Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/login "HTTP/2 303 See Other" [httpx]
2025-08-02T04:21:19.592994Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/oauth/authorize?state=06c38c06-bcda-4214-95c7-c673c1c452af "HTTP/2 303 See Other" [httpx]
2025-08-02T04:21:19.727666Z [info     ] HTTP Request: GET https://accounts.antibodyregistry.org/auth/realms/areg/protocol/openid-connect/auth?access_type=online&client_id=web-client&redirect_uri=https%3A%2F%2Fwww.antibodyregistry.org%2Foauth%2Fcallback&response_type=code&scope=openid+email+profile&state=06c38c06-bcda-4214-95c7-c673c1c452af "HTTP/2 200 OK" [httpx]
2025-08-02T04:21:19.803383Z [info     ] HTTP Request: POST https://accounts.antibodyregistry.org/auth/realms/areg/login-actions/authenticate?session_code=H1MWl0jYGl2NyBL4sr1fiNd-SfZiiQjJ7XR9xHiKFNQ&execution=efc751e8-55c5-4631-9faa-712e26fec296&client_id=web-client&tab_id=wuQTA8M4jy4 "HTTP/2 302 Found" [httpx]
2025-08-02T04:21:19.958244Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/oauth/callback?state=06c38c06-bcda-4214-95c7-c673c1c452af&session_state=08dc3f8c-0249-4d79-a265-ffd9ff4349ff&code=d640023e-05e7-46a6-bbde-c11c5021f5b6.08dc3f8c-0249-4d79-a265-ffd9ff4349ff.111caf43-3d26-484d-8dc9-7fa911ac221c "HTTP/2 303 See Other" [httpx]
2025-08-02T04:21:20.004971Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/login "HTTP/2 200 OK" [httpx]
2025-08-02T04:21:21.975299Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/api/antibodies?size=500&page=2 "HTTP/2 200 OK" [httpx]
2025-08-02T04:21:22.184774Z [info     ] write_begin                    [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 2} path=PosixPath('output/2.xz')
2025-08-02T04:21:22.249379Z [info     ] fetch_begin                    [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 3} path=PosixPath('output/3.xz')
2025-08-02T04:21:24.144106Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/api/antibodies?size=500&page=3 "HTTP/2 200 OK" [httpx]
2025-08-02T04:21:24.387959Z [info     ] write_begin                    [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 3} path=PosixPath('output/3.xz')
…
```
