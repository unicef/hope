import ApolloClient from 'apollo-client';
import { createUploadLink } from 'apollo-upload-client';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { onError } from 'apollo-link-error';
import { ApolloLink } from 'apollo-link';
import { GRAPHQL_URL } from '../config';

const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors)
    graphQLErrors.forEach(({ message }) => {
      if (message.toLowerCase().includes('user is not authenticated')) {
        window.location.replace('/login');
      }
    });

  // eslint-disable-next-line no-console
  if (networkError) console.error(`[Network error]: ${networkError}`);
});
const link = ApolloLink.from([
  errorLink,
  createUploadLink({ uri: GRAPHQL_URL }),
]);

export const client = new ApolloClient({
  cache: new InMemoryCache(),
  link,
});
