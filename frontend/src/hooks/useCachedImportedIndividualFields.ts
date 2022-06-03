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
import { useEffect, useState } from 'react';
import localForage from 'localforage';

function utf8tob64(str) {
  return window.btoa(unescape(encodeURIComponent(str)));
}

function b64toutf8(str) {
  return decodeURIComponent(escape(window.atob(str)));
}
export function useCachedImportedIndividualFieldsQuery(businessArea) {
  const [loading, setLoading] = useState(true);
  const [cache, setCache] = useState(undefined);
  const [getAttributes, results] = useImportedIndividualFieldsLazyQuery({
    variables: {
      businessAreaSlug: businessArea,
    },
  });
  useEffect(() => {
    if (cache === null) {
      getAttributes();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cache]);
  useEffect(() => {
    console.log('results.loading', results.loading);
    if (results.data || results.error) {
      setLoading(results.loading);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [results.loading]);

  useEffect(() => {
    localForage
      .getItem(`cache-targeting-core-fields-attributes-${businessArea}`)
      .then((value) => {
        console.log('get cache',value)
        if (value) {
          setCache(JSON.parse(value as string));
        } else {
          setCache(null);
        }
      });
  }, [businessArea]);

  return { data: results.data, loading, error: results.error };
}
