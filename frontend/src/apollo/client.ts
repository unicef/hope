import ApolloClient from 'apollo-client';
import { createUploadLink } from 'apollo-upload-client';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { GRAPHQL_URL } from '../config';

export const client = new ApolloClient({
  cache: new InMemoryCache(),
  link: createUploadLink({ uri: GRAPHQL_URL }),
});
