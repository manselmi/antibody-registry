<!-- vim: set ft=markdown : -->


# Antibody Registry login

## Summary

The script `antibody_registry_login.py` demonstrates automated headless login to the Antibody
Registry with [`httpx`](https://www.python-httpx.org/) by implementing a [custom authentication
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
pixi run -- ./antibody_registry_login.py
```

### Output

``` text
2025-03-18T20:18:01.307942Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/api/antibodies?size=10&page=51 "HTTP/2 401 Unauthorized" [httpx]
2025-03-18T20:18:03.309825Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/login "HTTP/2 303 See Other" [httpx]
2025-03-18T20:18:03.354456Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/oauth/authorize?state=33818307-23c0-4bff-a19f-51d4668da8de "HTTP/2 303 See Other" [httpx]
2025-03-18T20:18:03.485704Z [info     ] HTTP Request: GET https://accounts.antibodyregistry.org/auth/realms/areg/protocol/openid-connect/auth?access_type=online&client_id=web-client&redirect_uri=https%3A%2F%2Fwww.antibodyregistry.org%2Foauth%2Fcallback&response_type=code&scope=openid+email+profile&state=33818307-23c0-4bff-a19f-51d4668da8de "HTTP/2 200 OK" [httpx]
2025-03-18T20:18:03.594480Z [info     ] HTTP Request: POST https://accounts.antibodyregistry.org/auth/realms/areg/login-actions/authenticate?session_code=ac_Qpj8bu8JsRyFqz3QWVJeBCplADewlogvCjoSDY8c&execution=efc751e8-55c5-4631-9faa-712e26fec296&client_id=web-client&tab_id=ePx64GuAhtg "HTTP/2 302 Found" [httpx]
2025-03-18T20:18:03.677347Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/oauth/callback?state=33818307-23c0-4bff-a19f-51d4668da8de&session_state=a83aff13-c172-4786-ae31-1f4e72c31a75&code=16c523b3-0837-43cd-a8ea-cbd3c03017b7.a83aff13-c172-4786-ae31-1f4e72c31a75.111caf43-3d26-484d-8dc9-7fa911ac221c "HTTP/2 303 See Other" [httpx]
2025-03-18T20:18:03.797296Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/login "HTTP/2 200 OK" [httpx]
2025-03-18T20:18:05.391296Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/api/antibodies?size=10&page=51 "HTTP/2 200 OK" [httpx]
2025-03-18T20:18:06.733296Z [info     ] HTTP Request: GET https://www.antibodyregistry.org/api/antibodies?size=10&page=52 "HTTP/2 200 OK" [httpx]
```
