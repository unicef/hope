const indent = 4;

module.exports = {
    extends: [
        'airbnb-typescript/base',
        'plugin:cypress/recommended',
        'prettier',
        'prettier/@typescript-eslint',
    ],
    rules: {
        indent: ['error', indent],
        '@typescript-eslint/indent': ['error', indent],
    },
    parserOptions: {
        project: './tsconfig.json',
    },
};
