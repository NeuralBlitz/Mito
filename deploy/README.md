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

## API authentication (new default: strict)

Mito now defaults to `MITO_AUTH_MODE=strict`. Protected API endpoints deny
requests when API key or JWT verification is not configured. Requests require
both `X-API-Key` and a verified Bearer JWT. The `/` health endpoint remains
public. The `/tools` and `/metrics` endpoints now require the API key.

Configure `MITO_API_KEY` to a strong random secret and choose **one** signing
mechanism: `MITO_JWT_SECRET` for HS256, or an RS256 private/public key pair
(`MITO_JWT_PRIVATE_KEY`, `MITO_JWT_PUBLIC_KEY`). Never commit secrets.

To issue tokens, configure `MITO_JWT_USERS` as a JSON map from username to
PBKDF2-SHA256 verifier. Generate a verifier locally with
`python3 scripts/hash_password.py` and store it in a secrets manager.
The verifier format is
`pbkdf2_sha256$260000$<hex_salt>$<hex_digest>`. Plaintext user entries
and the legacy `MITO_JWT_PASSWORD` setting are not accepted.

Use `POST /token` with the API key and OAuth2 password form to obtain a JWT;
the token is then used with the API key on inference requests. `POST
/token/refresh` requires an existing valid JWT and the API key. Issued
bearer tokens expire; clients must refresh or authenticate again.

For local debugging only, set `MITO_AUTH_MODE=development` explicitly.
Authentication bypass applies **only** when the direct request client is
`127.0.0.1` or `::1`, not merely because the forwarded host header or
reverse proxy says localhost. This mode must not be used in production.
Docker bridge clients are normally not loopback, so they still require
authentication.

Browser cross-origin requests are denied by default. To allow a specific
browser frontend, set `MITO_CORS_ORIGINS` to a comma-separated list of
trusted origins such as `https://app.example.com`; do not use a wildcard.

**Breaking change:** clients that previously relied on missing API keys,
raw bearer-token passthrough, plaintext JWT user credentials, or permissive
CORS must explicitly migrate before upgrading. Test behind the loopback
binding before exposing the service. External deployment still requires
TLS, a secret manager, rate limiting review and independent security testing.

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
