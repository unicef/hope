import { QueryResult, WatchQueryFetchPolicy } from '@apollo/client';
import { MeQuery, MeQueryVariables, useMeQuery } from '@generated/graphql';

export function useCachedMe(): QueryResult<MeQuery, MeQueryVariables> {
  const meFetchedTimestamp =
    Number.parseInt(localStorage.getItem('me-fetched-timestamp'), 10) || 0;
  const ttlCashAndNetwork = 5 * 60 * 1000;
  const ttlForceNetwork = 60 * 60 * 1000;
  const timeDiff = Date.now() - meFetchedTimestamp;
  let fetchPolicy: WatchQueryFetchPolicy = 'network-only';
  if (timeDiff < ttlForceNetwork) {
    fetchPolicy = 'cache-first';
  } else if (timeDiff < ttlCashAndNetwork) {
    fetchPolicy = 'cache-and-network';
  } else {
    localStorage.setItem('me-fetched-timestamp', Date.now().toString());
  }
  return useMeQuery({
    fetchPolicy,
  });
}
