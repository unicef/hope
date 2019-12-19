module.exports = {
  'import/no-extraneous-dependencies': [2, {}],
  'import/order': [
    1,
    {
      groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
      'newlines-between': 'never',
    },
  ],
  'import/extensions': 0,
};
