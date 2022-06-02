import {
  MeQuery,
  MeQueryVariables,
  useImportedIndividualFieldsLazyQuery,
  useImportedIndividualFieldsQuery,
  useMeQuery,
} from '../__generated__/graphql';
import { WatchQueryFetchPolicy } from 'apollo-client';
// eslint-disable-next-line import/no-extraneous-dependencies
import { QueryResult } from '@apollo/react-common';
import { useEffect } from 'react';

export function useCachedImportedIndividualFieldsQuery(businessArea) {
  const cachedData = localStorage.getItem(
    'cache-targeting-core-fields-attributes',
  );
  const [
    getAttributes,
    { data, loading, error },
  ] = useImportedIndividualFieldsLazyQuery({
    variables: {
      businessAreaSlug: businessArea,
    },
  });
  useEffect(() => {
    if (!cachedData) {
      getAttributes();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return { data, loading, error };
}
