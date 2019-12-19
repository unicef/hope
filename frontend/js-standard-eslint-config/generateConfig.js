const importRules = require('./rules/import');
const typescriptOverride = require('./rules/typescript');
const reactRules = require('./rules/react');
const jestRules = require('./rules/jest');

module.exports = ({
  react,
  typescript,
  nodePaths = undefined,
} = {}) => ({
  extends: [
    react ? 'airbnb' : 'airbnb-base',
    'plugin:jest/recommended',
    'plugin:jest/style',
    'prettier',
    ...(react ? ['airbnb/hooks', 'prettier/react'] : []),
  ],
  rules: {
    ...importRules,
    ...jestRules,
    ...(react ? reactRules : {}),
  },
  settings: {
    parserOptions: {
      ecmaFeatures: {
        jsx: true,
      },
      ecmaVersion: 2019,
    },
    'import/resolver': {
      node: {
        paths: nodePaths,
      },
    },
  },
  overrides: [
    ...(typescript ? [typescriptOverride()] : []),
  ],
});
