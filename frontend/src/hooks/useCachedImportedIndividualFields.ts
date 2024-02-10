/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useState } from 'react';
import localForage from 'localforage';
import { ApolloError } from 'apollo-client';
import {
  ImportedIndividualFieldsQuery,
  useImportedIndividualFieldsLazyQuery,
} from '../__generated__/graphql';

export function useCachedImportedIndividualFieldsQuery(
  businessArea, selectedProgramName
): {
  loading: boolean;
  data: ImportedIndividualFieldsQuery;
  error: ApolloError;
} {
  const [loading, setLoading] = useState(true);
  const [oldBusinessArea, setOldBusinessArea] = useState('');
  const [oldSelectedProgramName, setOldSelectedProgramName] = useState('');
  const [cache, setCache] = useState(null);

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
    if (businessArea === oldBusinessArea && selectedProgramName === oldSelectedProgramName) {
      return;
    }
    setOldBusinessArea(businessArea);
    setOldSelectedProgramName(selectedProgramName);
    localForage
      .getItem(`cache-targeting-core-fields-attributes-${businessArea}`)
      .then((value) => {
        if (value) {
          setCache(value);
        }
      });
  }, [businessArea, selectedProgramName]);
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
