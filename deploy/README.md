# Mito deployment notes

## Local API container

From the repository root:

```sh
docker compose -f deploy/docker-compose.yml up --build
```

The Compose build context is the repository root. The API binds to
`127.0.0.1:8000` by default, and is **not** externally reachable.

The image imports repository sources through `PYTHONPATH=/app`.
There is no Python package manifest at the root, so `pip install .`
is intentionally not called.

## Security status

The server permits requests without an API key when `MITO_API_KEY` is unset.
JWT authentication and deployment security require independent review before
exposing this service to untrusted networks. Binding to localhost is not
a substitute for production hardening.

## Background workers

The former worker command (`python -m mito worker`) does not correspond to
a supported CLI subcommand or importable Python module, so the default
Compose configuration starts only the API. A worker should be reintroduced
after an actual worker entry point, tests, and health checks are implemented.

## Test coverage

GitHub Actions runs C++ CLI smoke tests and lightweight FastAPI import/route
tests, but not model inference, full Docker builds, or the full Python suite.
On a fully provisioned environment, `make test` now propagates pytest
errors rather than printing an erroneous success message.
