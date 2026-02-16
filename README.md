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
    pixi run -- prek-install
    ```

## Example

### Invocation

``` shell
pixi run -- ./download.py
```

### Output

``` text
2025-08-02T22:27:12.013186Z [info     ] fetch_begin                    [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 1}
2025-08-02T22:27:12.653698Z [info     ] fetch_end                      [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') current_element=500 params={'size': 500, 'page': 1} status_code=200 total_elements=3165751
2025-08-02T22:27:12.653840Z [info     ] write_begin                    [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 1} path=PosixPath('output/1.xz')
2025-08-02T22:27:12.713354Z [info     ] write_end                      [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 1} path=PosixPath('output/1.xz')
2025-08-02T22:27:12.713554Z [info     ] fetch_begin                    [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 2}
2025-08-02T22:27:14.404534Z [info     ] fetch_end                      [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') current_element=1000 params={'size': 500, 'page': 2} status_code=200 total_elements=3165751
2025-08-02T22:27:14.404679Z [info     ] write_begin                    [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 2} path=PosixPath('output/2.xz')
2025-08-02T22:27:14.467674Z [info     ] write_end                      [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 2} path=PosixPath('output/2.xz')
2025-08-02T22:27:14.467956Z [info     ] fetch_begin                    [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 3}
2025-08-02T22:27:16.617738Z [info     ] fetch_end                      [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') current_element=1500 params={'size': 500, 'page': 3} status_code=200 total_elements=3165751
2025-08-02T22:27:16.617861Z [info     ] write_begin                    [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 3} path=PosixPath('output/3.xz')
2025-08-02T22:27:16.676705Z [info     ] write_end                      [__main__] base_url=URL('https://www.antibodyregistry.org/api/antibodies') params={'size': 500, 'page': 3} path=PosixPath('output/3.xz')
…
```
