/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useState } from 'react';
import {
  ImportDataStatus,
  KoboImportDataQueryResult,
  SaveKoboImportDataAsyncMutationVariables,
  useKoboImportDataLazyQuery,
  useSaveKoboImportDataAsyncMutation,
} from '@generated/graphql';
import { useLazyInterval } from '@hooks/useInterval';

export interface UseSaveKoboImportDataAndCheckStatusReturnType {
  saveAndStartPolling: (
    variables: SaveKoboImportDataAsyncMutationVariables,
  ) => Promise<void>;
  stopPollingImportData: () => void;
  loading: boolean;
  koboImportData: KoboImportDataQueryResult['data']['koboImportData'];
}

export function useSaveKoboImportDataAndCheckStatus(): UseSaveKoboImportDataAndCheckStatusReturnType {
  const [loading, setLoading] = useState(false);
  const [saveKoboImportDataMutate, { data: koboImportDataFromMutation }] =
    useSaveKoboImportDataAsyncMutation();
  const [loadImportData, { data: koboImportData }] = useKoboImportDataLazyQuery(
    {
      variables: {
        id: koboImportDataFromMutation?.saveKoboImportDataAsync?.importData?.id,
      },
      fetchPolicy: 'network-only',
    },
  );
  const [startPollingImportData, stopPollingImportData] = useLazyInterval(
    (args) =>
      loadImportData({
        variables: {
          id: args.id,
        },
      }),
    3000,
  );
  useEffect(() => {
    if (koboImportDataFromMutation?.saveKoboImportDataAsync?.importData) {
      startPollingImportData({
        id: koboImportDataFromMutation.saveKoboImportDataAsync.importData.id,
      });
    }
  }, [koboImportDataFromMutation?.saveKoboImportDataAsync?.importData]);
  useEffect(() => {
    if (!koboImportData) {
      return;
    }
    if (
      [
        ImportDataStatus.Error,
        ImportDataStatus.ValidationError,
        ImportDataStatus.Finished,
      ].includes(koboImportData?.koboImportData?.status)
    ) {
      stopPollingImportData();
      setLoading(false);
    }
  }, [koboImportData]);
  const saveAndStartPolling = async (
    variables: SaveKoboImportDataAsyncMutationVariables,
  ): Promise<void> => {
    try {
      setLoading(true);
      await saveKoboImportDataMutate({ variables });
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };
  return {
    saveAndStartPolling,
    stopPollingImportData,
    loading,
    koboImportData: koboImportData?.koboImportData,
  };
}
