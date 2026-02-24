<!-- vim: set ft=markdown : -->


# Antibody Registry downloader

## Summary

The script `download.py` demonstrates automated headless login to the Antibody Registry
with [`httpx`](https://www.python-httpx.org/) by implementing a [custom authentication
scheme](https://www.python-httpx.org/advanced/authentication/#custom-authentication-schemes).

## Prerequisites

* [mise](https://mise.jdx.dev/)

* Antibody Registry username and password in the environment variables `ANTIBODY_REGISTRY_USERNAME`
  and `ANTIBODY_REGISTRY_PASSWORD`, respectively. Override `fnox.toml` with `fnox.local.toml`.

    * [fnox](https://fnox.jdx.dev/)

``` shell
mise run install
```

## Example

### Invocation

``` shell
mise run
```

### Output

``` text
2026-02-24T17:46:46.097454Z [info     ] fetch_begin                    [__main__] base_url=https://www.antibodyregistry.org/api/antibodies params={'size': 500, 'page': 1}
2026-02-24T17:46:49.905613Z [info     ] fetch_end                      [__main__] base_url=https://www.antibodyregistry.org/api/antibodies current_element=500 params={'size': 500, 'page': 1} status_code=200 total_elements=3174639
2026-02-24T17:46:49.906002Z [info     ] write_begin                    [__main__] base_url=https://www.antibodyregistry.org/api/antibodies params={'size': 500, 'page': 1} path=output/1.xz
2026-02-24T17:46:49.963930Z [info     ] write_end                      [__main__] base_url=https://www.antibodyregistry.org/api/antibodies params={'size': 500, 'page': 1} path=output/1.xz
2026-02-24T17:46:49.964125Z [info     ] fetch_begin                    [__main__] base_url=https://www.antibodyregistry.org/api/antibodies params={'size': 500, 'page': 2}
2026-02-24T17:46:53.789570Z [info     ] fetch_end                      [__main__] base_url=https://www.antibodyregistry.org/api/antibodies current_element=1000 params={'size': 500, 'page': 2} status_code=200 total_elements=3174639
2026-02-24T17:46:53.789914Z [info     ] write_begin                    [__main__] base_url=https://www.antibodyregistry.org/api/antibodies params={'size': 500, 'page': 2} path=output/2.xz
2026-02-24T17:46:53.836948Z [info     ] write_end                      [__main__] base_url=https://www.antibodyregistry.org/api/antibodies params={'size': 500, 'page': 2} path=output/2.xz
2026-02-24T17:46:53.837131Z [info     ] fetch_begin                    [__main__] base_url=https://www.antibodyregistry.org/api/antibodies params={'size': 500, 'page': 3}
2026-02-24T17:47:00.813162Z [info     ] fetch_end                      [__main__] base_url=https://www.antibodyregistry.org/api/antibodies current_element=1500 params={'size': 500, 'page': 3} status_code=200 total_elements=3174639
2026-02-24T17:47:00.813471Z [info     ] write_begin                    [__main__] base_url=https://www.antibodyregistry.org/api/antibodies params={'size': 500, 'page': 3} path=output/3.xz
2026-02-24T17:47:00.875993Z [info     ] write_end                      [__main__] base_url=https://www.antibodyregistry.org/api/antibodies params={'size': 500, 'page': 3} path=output/3.xz
…
```
