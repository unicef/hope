/* eslint-disable react-hooks/exhaustive-deps */
import { ApolloError } from '@apollo/client';
import {
  IndividualFieldsQuery,
  useIndividualFieldsLazyQuery,
} from '@generated/graphql';
import localForage from 'localforage';
import { useEffect, useState } from 'react';

export function useCachedIndividualFieldsQuery(
  businessArea,
  selectedProgramId,
): {
  loading: boolean;
  data: IndividualFieldsQuery;
  error: ApolloError;
} {
  const [loading, setLoading] = useState(true);
  const [oldBusinessArea, setOldBusinessArea] = useState('');
  const [oldSelectedProgramId, setOldSelectedProgramId] = useState('');
  const [cache, setCache] = useState(null);

  const lastUpdatedTimestamp =
    Number.parseInt(
      localStorage.getItem(
        `cache-targeting-core-fields-attributes-${businessArea}-${selectedProgramId}-timestamp`,
      ),
      10,
    ) || 0;
  const ttl = 2 * 60 * 60 * 1000;
  const [getAttributes, results] = useIndividualFieldsLazyQuery();

  useEffect(() => {
    if (Date.now() - lastUpdatedTimestamp < ttl) {
      return;
    }
    getAttributes({
      variables: {
        businessAreaSlug: businessArea,
        programId: selectedProgramId,
      },
    });
  }, [businessArea, selectedProgramId]);

  useEffect(() => {
    if (results.data || results.error) {
      setLoading(results.loading);
    }
  }, [results.loading]);

  useEffect(() => {
    if (
      businessArea === oldBusinessArea &&
      selectedProgramId === oldSelectedProgramId
    ) {
      return;
    }
    setOldBusinessArea(businessArea);
    setOldSelectedProgramId(selectedProgramId);
    localForage
      .getItem(
        `cache-targeting-core-fields-attributes-${businessArea}-${selectedProgramId}`,
      )
      .then((value) => {
        if (value) {
          setCache(value);
        }
      });
  }, [businessArea, selectedProgramId]);
  useEffect(() => {
    if (!results.data) {
      return;
    }
    localForage.setItem(
      `cache-targeting-core-fields-attributes-${businessArea}-${selectedProgramId}`,
      results.data,
    );
    localStorage.setItem(
      `cache-targeting-core-fields-attributes-${businessArea}-${selectedProgramId}-timestamp`,
      Date.now().toString(),
    );
  }, [results.data]);

  if (cache) {
    return { data: cache, loading: false, error: null };
  }
  return { data: results.data, loading, error: results.error };
}
