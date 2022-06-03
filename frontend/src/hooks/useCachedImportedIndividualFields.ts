/* eslint-disable react-hooks/exhaustive-deps */
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
  const [oldBusinessArea, setOldBusinessArea] = useState('');
  const [cache, setCache] = useState(null);
  const [needToRefreshCash, setNeedToRefreshCash] = useState(false);
  const lastUpdatedTimestamp =
    Number.parseInt(
      localStorage.getItem(
        `cache-targeting-core-fields-attributes-${businessArea}-timestamp`,
      ),
      10,
    ) || 0;
  const ttl = 2 * 60 * 60 * 1000;
  const [getAttributes, results] = useImportedIndividualFieldsLazyQuery({
    variables: {
      businessAreaSlug: businessArea,
    },
  });
  useEffect(() => {
    if (Date.now() - lastUpdatedTimestamp < ttl) {
      return;
    }
    getAttributes();
  }, []);
  useEffect(() => {
    if (results.data || results.error) {
      setLoading(results.loading);
    }
  }, [results.loading]);

  useEffect(() => {
    if (businessArea === oldBusinessArea) {
      return;
    }
    setOldBusinessArea(businessArea);
    localForage
      .getItem(`cache-targeting-core-fields-attributes-${businessArea}`)
      .then((value) => {
        if (value) {
          setCache(value);
        }
        setNeedToRefreshCash(true);
      });
  }, [businessArea]);
  useEffect(() => {
    if (!results.data) {
      return;
    }
    localForage.setItem(
      `cache-targeting-core-fields-attributes-${businessArea}`,
      results.data,
    );
    localStorage.setItem(
      `cache-targeting-core-fields-attributes-${businessArea}-timestamp`,
      Date.now().toString(),
    );
  }, [results.data]);

  if (cache) {
    return { data: cache, loading: false, error: null };
  }
  return { data: results.data, loading, error: results.error };
}
