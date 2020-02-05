import ApolloClient from 'apollo-client';
import { createUploadLink } from 'apollo-upload-client';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { GRAPHQL_URL } from '../config';
import { onError } from 'apollo-link-error';
import { ApolloLink } from 'apollo-link';

const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors)
    graphQLErrors.forEach(({ message, locations, path }) => {
      if (message.toLowerCase().includes('user is not authenticated')) {
        window.location.replace('/login');
      }
    });

  if (networkError) console.log(`[Network error]: ${networkError}`);
});
const link = ApolloLink.from([
  errorLink,
  createUploadLink({ uri: GRAPHQL_URL }),
]);

export const client = new ApolloClient({
  cache: new InMemoryCache(),
  link,
});
