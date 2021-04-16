import ApolloClient from 'apollo-client';
import { createUploadLink } from 'apollo-upload-client';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { onError } from 'apollo-link-error';
import { ApolloLink } from 'apollo-link';
import { GraphQLError } from 'graphql';
import { GRAPHQL_URL } from '../config';

export class ValidationGraphQLError extends GraphQLError {
  validationErrors;
}
const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors)
    graphQLErrors.forEach(({ message }) => {
      if (message.toLowerCase().includes('user is not authenticated')) {
        window.location.replace(
          `/login?next=${window.location.pathname}${window.location.search}`,
        );
      }
      if (
        message.toLowerCase().includes('user does not have correct permission')
      ) {
        // eslint-disable-next-line no-console
        console.error(`Permission denied for mutation`);
      }
    });

  // eslint-disable-next-line no-console
  if (networkError) console.error(`[Network error]: ${networkError}`);
});
function findValidationErrors(
  data,
  name = 'ROOT',
  errors: { [key: string]: { [fieldName: string]: string } } = {},
): { [key: string]: { [fieldName: string]: string } } {
  if (!data) {
    return errors;
  }
  // debugger;
  for (const entry of Object.entries(data)) {
    if (entry[0] === 'validationErrors' && entry[1]) {
      // eslint-disable-next-line no-param-reassign
      errors[name] = entry[1] as { [fieldName: string]: string };
      // eslint-disable-next-line no-continue
      continue;
    }
    if (typeof data === 'object' && data !== null) {
      findValidationErrors(entry[1], entry[0], errors);
    }
  }
  return errors;
}
const validationErrorMiddleware = new ApolloLink((operation, forward) => {
  return forward(operation).map((response) => {
    if (response.data) {
      const context = operation.getContext();
      const {
        response: { headers },
      } = context;
      if (headers) {
        // eslint-disable-next-line @typescript-eslint/no-use-before-define
        client.writeData({
          data: { backendVersion: headers.get('X-Hope-Backend-Version') },
        });
      }
    }
    if (response.errors) {
      return response;
    }
    const validationErrors = findValidationErrors(response?.data);
    if (Object.keys(validationErrors).length > 0) {
      const error = new ValidationGraphQLError(
        JSON.stringify(validationErrors),
      );
      error.validationErrors = validationErrors;
      response.errors = [error];
    }
    return response;
  });
});
const link = ApolloLink.from([
  validationErrorMiddleware,
  errorLink,
  createUploadLink({ uri: GRAPHQL_URL }),
]);

export const client = new ApolloClient({
  cache: new InMemoryCache(),
  link,
});
