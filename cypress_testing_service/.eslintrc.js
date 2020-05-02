module.exports = {
  extends: [
    'airbnb-typescript/base',
    'plugin:cypress/recommended',
    'prettier',
    'prettier/@typescript-eslint',
  ],
  rules: {
    indent: ['error', 2],
    '@typescript-eslint/indent': ['error', 2],
  },
  parserOptions: {
    project: './tsconfig.json',
  },
};
