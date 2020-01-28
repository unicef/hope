module.exports = {
  client: {
    includes: ['./src/apollo/**/*.js'],
    service: {
      name: 'htc-mis',
      localSchemaFile: './data/schema.graphql'
    },
  },
};
