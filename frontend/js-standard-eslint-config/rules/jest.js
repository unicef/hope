module.exports = {
  'jest/lowercase-name': [1, { ignore: ['describe'] }],
  'jest/expect-expect': [
    1,
    {
      assertFunctionNames: ['expect', 'expectObservable'],
    },
  ],
};
