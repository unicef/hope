const { defineConfig, globalIgnores } = require('eslint/config');

const tsParser = require('@typescript-eslint/parser');
const globals = require('globals');

const { fixupConfigRules, fixupPluginRules } = require('@eslint/compat');

const typescriptEslint = require('@typescript-eslint/eslint-plugin');
const react = require('eslint-plugin-react');
const _import = require('eslint-plugin-import');
const reactHooks = require('eslint-plugin-react-hooks');
const tanstackQuery = require('@tanstack/eslint-plugin-query');
const js = require('@eslint/js');

const { FlatCompat } = require('@eslint/eslintrc');

const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

module.exports = defineConfig([
  {
    languageOptions: {
      parser: tsParser,

      globals: {
        ...globals.browser,
        ...globals.node,
      },

      sourceType: 'module',

      parserOptions: {
        tsconfigRootDir: __dirname,
        project: './tsconfig.json',

        ecmaFeatures: {
          node: true,
          es6: true,
        },
      },
    },

    extends: fixupConfigRules(
      compat.extends(
        'eslint:recommended',
        'plugin:@typescript-eslint/recommended',
        'plugin:@typescript-eslint/recommended-requiring-type-checking',
        'plugin:react/recommended',
        'plugin:import/errors',
        'plugin:import/warnings',
        'plugin:@tanstack/eslint-plugin-query/recommended',
      ),
    ),

    plugins: {
      '@typescript-eslint': fixupPluginRules(typescriptEslint),
      react: fixupPluginRules(react),
      import: fixupPluginRules(_import),
      'react-hooks': fixupPluginRules(reactHooks),
      '@tanstack/query': fixupPluginRules(tanstackQuery),
      'unused-imports': require('eslint-plugin-unused-imports'),
    },

    settings: {
      react: {
        version: 'detect',
      },

      'import/resolver': {
        alias: {
          map: [['@', './src']],
        },
      },
    },

    rules: {
      'unused-imports/no-unused-imports': 'error',
      'unused-imports/no-unused-vars': [
        'warn',
        {
          vars: 'all',
          varsIgnorePattern: '^_',
          args: 'after-used',
          argsIgnorePattern: '^_',
        },
      ],
      '@typescript-eslint/brace-style': 'off',
      'object-curly-spacing': ['error', 'always'],
      'brace-style': ['error', '1tbs', { allowSingleLine: true }],
      '@typescript-eslint/comma-dangle': 'off',
      'comma-dangle': ['error', 'always-multiline'],
      '@typescript-eslint/comma-spacing': 'off',
      'comma-spacing': ['error', { before: false, after: true }],
      '@typescript-eslint/func-call-spacing': 'off',
      'func-call-spacing': ['error', 'never'],
      '@typescript-eslint/keyword-spacing': 'off',
      'keyword-spacing': ['error', { before: true, after: true }],
      '@typescript-eslint/lines-between-class-members': 'off',
      'lines-between-class-members': [
        'error',
        'always',
        { exceptAfterSingleLine: true },
      ],
      '@typescript-eslint/no-extra-semi': 'off',
      'no-extra-semi': ['error'],
      '@typescript-eslint/space-before-blocks': 'off',
      'space-before-blocks': ['error', 'always'],
      '@typescript-eslint/no-throw-literal': 'off',
      'no-throw-literal': ['error'],
      '@typescript-eslint/quotes': 'off',
      quotes: ['error', 'single', { avoidEscape: true }],
      '@typescript-eslint/semi': 'off',
      semi: ['error', 'always'],
      '@typescript-eslint/space-before-function-paren': 'off',
      'space-before-function-paren': 'off',
      '@typescript-eslint/space-infix-ops': 'off',
      'space-infix-ops': ['error'],
      '@typescript-eslint/ban-ts-comment': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/indent': 'off',
      '@typescript-eslint/naming-convention': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-floating-promises': 'off',
      '@typescript-eslint/no-redundant-type-constituents': 'off',
      '@typescript-eslint/no-unsafe-argument': 'off',
      '@typescript-eslint/no-unsafe-assignment': 'off',
      '@typescript-eslint/no-unsafe-call': 'off',
      '@typescript-eslint/no-unsafe-enum-comparison': 'off',
      '@typescript-eslint/no-unsafe-member-access': 'off',
      '@typescript-eslint/no-unsafe-return': 'off',
      '@typescript-eslint/no-misused-promises': 'off',
      '@typescript-eslint/no-unused-vars': 'warn',
      'func-call-spacing': 'off',
      'no-unused-vars': 'off',
      'no-undef': 'error',
      'import/no-unresolved': 'off',
      'import/named': 'off',
      'import/default': 'off',
      'import/namespace': 'off',
      'import/no-extraneous-dependencies': 'off',
      'import/prefer-default-export': 'off',
      'react-hooks/exhaustive-deps': 'warn',
      'react-hooks/rules-of-hooks': 'error',
      '@tanstack/query/exhaustive-deps': 'error',
      '@tanstack/query/no-rest-destructuring': 'warn',
      '@tanstack/query/stable-query-client': 'error',

      'react/jsx-filename-extension': [
        1,
        {
          extensions: ['.js', '.jsx', '.ts', '.tsx'],
        },
      ],

      'react/prop-types': 'off',
      'react/react-in-jsx-scope': 'off',
      'import/extensions': 'off',
      'import/no-named-as-default': 'off',
      'import/no-named-as-default-member': 'off',

      '@typescript-eslint/unbound-method': [
        'error',
        {
          ignoreStatic: true,
        },
      ],

      'padding-line-between-statements': [
        'error',
        {
          blankLine: 'never',
          prev: 'import',
          next: 'import',
        },
      ],
    },
  },
  globalIgnores([
    '**/*.test.tsx',
    '**/*.test.ts',
    '**/__generated__/*',
    'src/restgenerated/',
    '**/node_modules/',
  ]),
  globalIgnores(['**/.eslintrc.cjs', '**/node_modules/']),
]);
