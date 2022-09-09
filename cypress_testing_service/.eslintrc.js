module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  extends: [
    'airbnb-typescript/base',
    'plugin:cypress/recommended',
    'prettier',
    'prettier/@typescript-eslint',
    "eslint:recommended",
    "plugin:import/recommended"
  ],
  rules: {
    indent: ['error', 2],
    '@typescript-eslint/indent': ['error', 2],
    semi: ['error', 'always'],
    "no-unused-expressions": 0,
    'no-plusplus': 'off',
    "spaced-comment": ["error", "always", { "markers": ["/"] }],
    "class-methods-use-this": ["off"],
    "no-unused-vars": "off",
    "@typescript-eslint/no-unused-vars": "off",
    "@typescript-eslint/no-loop-func": ["off"],
    "@typescript-eslint/object-curly-spacing": "off",
    "no-redeclare": [2, { "builtinGlobals": true }],
    "no-var": 0
  },
  overrides: [
    {
      files: ['*.ts', '*.tsx'], // Your TypeScript files extension
    }],
  parserOptions: {
    project: './tsconfig.json',
    tsconfigRootDir: __dirname,
    sourceType: "module",
  },
  "globals": {
    "globalThis": false, // means it is not writeable
    module: true,
    Chai: true,
    require: true,
    Loggable: true,
    Timeoutable: true,
    Withinable: true
  },
  "env": {
    "browser": true
  },
  ignorePatterns: ["/*.*"],
};
