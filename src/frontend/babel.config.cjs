/* eslint-disable */

module.exports = {
  presets: [
    ['@babel/preset-env', { targets: { node: 'current' } }], // Target current Node.js
    ['@babel/preset-react', { runtime: 'automatic' }], // For JSX
    '@babel/preset-typescript', // For TS
  ],
};
