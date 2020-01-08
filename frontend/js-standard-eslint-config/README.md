# @tivix/eslint-config

This package contains a root [ESLint](https://eslint.org/) config, with automatic support for [TypeScript](https://www.typescriptlang.org/) and [React](https://reactjs.org/).

## Methodology

### Style rules

As linting configs are often heavily debated, this config uses Prettier for most code-style choices.

The base config is [`eslint-config-airbnb`](https://github.com/airbnb/javascript/tree/master/packages/eslint-config-airbnb).

### TypeScript support

When working with TypeScript, the recommended rules from [`@typescript-eslint/eslint-plugin`](https://github.com/typescript-eslint/typescript-eslint/tree/master/packages/eslint-plugin#usage) are applied.

You should also ensure that your IDE is set up to run ESLint on TypeScript files. In VSCode, this setting is:

```json
  "eslint.validate": [
      "javascript",
      "javascriptreact",
      "typescript",
      "typescriptreact"
  ],
```

## Installation

To manually install, add this package to the `"extends"` array in your project’s [ESLint config](https://eslint.org/docs/user-guide/configuring).

```json
{
  "extends": ["@tivix/eslint-config/typescript-react"]
}
```

The following configs are available:

- `@tivix/typescript`
- `@tivix/typescript-react`
- `@tivix/react`
- `@tivix/eslint-config`

## Config generator

For advanced cases, you can use the exported `generateConfig` function to build a config.
