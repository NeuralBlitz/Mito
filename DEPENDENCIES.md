# JavaScript dependency policy

Mito uses **npm** as the canonical JavaScript package manager for both
the repository root and `desktop/`. Their committed `package-lock.json`
files are authoritative.

## Reproducible setup

From the repository root (Node.js 22, npm 10):

```sh
npm ci --ignore-scripts
cd desktop
npm ci --ignore-scripts
```

The `--ignore-scripts` option is intentional for the dependency validation
gate; component-specific native builds and launch tasks are validated separately.

## Updating dependencies

Change `package.json`, run `npm install --package-lock-only --ignore-scripts`,
and commit the resulting `package-lock.json` together with the manifest.

Do not edit generated lockfiles by hand or commit simultaneous root-level
Bun, pnpm, or Yarn lockfiles unless the repository explicitly adopts a
different package manager with reproducible CI support.

Mito's optional, Python-based AI stack is managed independently via
`requirements.txt` and the Python checks in GitHub Actions.
