# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type aware lint rules:

- Configure the top-level `parserOptions` property like this:

```js
export default {
  // other rules...
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    project: ['./tsconfig.json', './tsconfig.node.json'],
    tsconfigRootDir: __dirname,
  },
}
```

- Replace `plugin:@typescript-eslint/recommended` to `plugin:@typescript-eslint/recommended-type-checked` or `plugin:@typescript-eslint/strict-type-checked`
- Optionally add `plugin:@typescript-eslint/stylistic-type-checked`
- Install [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) and add `plugin:react/recommended` & `plugin:react/jsx-runtime` to the `extends` list

## Supply chain protections

Dependency installs are locked down in `bunfig.toml`, `.npmrc` and `package.json`:

- **No install scripts.** `ignoreScripts = true`, `ignore-scripts=true` and `"trustedDependencies": []` stop dependencies from running `preinstall`/`install`/`postinstall`/`prepare`. To let a package run its script, add it to `trustedDependencies` in a separate PR and explain why.
- **7-day release age.** `minimumReleaseAge` means Bun only picks package versions published at least 7 days ago (same as `exclude-newer` for uv on the backend). Dependabot uses the same 7-day `cooldown`. If you need a fresh security fix sooner, add the package to `minimumReleaseAgeExcludes` and remove it once the version is older than 7 days.
- **One Bun version.** `packageManager` in `package.json` pins Bun. CI reads it via `setup-bun`, and `docker/Dockerfile` uses the same image tag. Update all of these together.
- **Frozen lockfile.** CI and Docker run `bun install --frozen-lockfile`, and CI runs `bun audit`.

To get the same protection in other projects, put the same `[install]` settings in `~/.bunfig.toml` and `ignore-scripts=true` in `~/.npmrc`.
