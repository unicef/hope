import ApolloClient from 'apollo-client';
import { createUploadLink } from 'apollo-upload-client';
import { InMemoryCache, NormalizedCacheObject } from 'apollo-cache-inmemory';
import { onError } from 'apollo-link-error';
import { ApolloLink } from 'apollo-link';
import { persistCache } from 'apollo-cache-persist';
import localForage from 'localforage';
import { GRAPHQL_URL } from '../config';
import { clearCache } from '../utils/utils';
import { ValidationGraphQLError } from './ValidationGraphQLError';

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
        const backendVersion = headers.get('X-Hope-Backend-Version');
        const oldBackendVersion =
          localStorage.getItem('backend-version') || '0';
        if (backendVersion !== oldBackendVersion) {
          // eslint-disable-next-line @typescript-eslint/no-use-before-define
          clearCache();
          localStorage.setItem('backend-version', backendVersion);
        }
        // eslint-disable-next-line @typescript-eslint/no-use-before-define
        client.writeData({
          data: { backendVersion },
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

const addBusinessAreaHeaderMiddleware = new ApolloLink((operation, forward) => {
  operation.setContext({
    headers: {
      'Business-Area': window.location.pathname.split('/')[1],
    },
  });
  return forward(operation);
});

const link = ApolloLink.from([
  addBusinessAreaHeaderMiddleware,
  validationErrorMiddleware,
  errorLink,
  createUploadLink({ uri: GRAPHQL_URL }),
]);
let client;
export async function getClient(): Promise<
  ApolloClient<NormalizedCacheObject>
> {
  if (client) {
    return client;
  }
  const cacheInitializedTimestamp =
    Number.parseInt(localStorage.getItem('cache-initialized-timestamp'), 10) ||
    0;
  const cacheTtl = 2 * 24 * 60 * 60 * 1000;
  if (Date.now() - cacheInitializedTimestamp > cacheTtl) {
    await clearCache();
    setTimeout(() => {
      localStorage.setItem(
        'cache-initialized-timestamp',
        Date.now().toString(),
      );
    }, 1000);
  }
  const cache = new InMemoryCache();
  await persistCache({
    cache,
    // eslint-disable-next-line @typescript-eslint/ban-ts-ignore
    // @ts-ignore
    storage: localForage,
  });
  client = new ApolloClient({
    cache,
    link,
  });
  return client;
}
