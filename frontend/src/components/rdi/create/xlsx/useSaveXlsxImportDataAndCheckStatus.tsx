/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useState } from 'react';
import {
  ImportDataStatus,
  UploadImportDataXlsxFileAsyncMutationVariables,
  XlsxImportDataQueryResult,
  useUploadImportDataXlsxFileAsyncMutation,
  useXlsxImportDataLazyQuery,
} from '../../../../__generated__/graphql';
import { useLazyInterval } from '../../../../hooks/useInterval';

export interface UseSaveXlsxImportDataAndCheckStatusReturnType {
  saveAndStartPolling: (
    variables: UploadImportDataXlsxFileAsyncMutationVariables,
  ) => Promise<void>;
  stopPollingImportData: () => void;
  loading: boolean;
  xlsxImportData: XlsxImportDataQueryResult['data']['importData'];
}

export function useSaveXlsxImportDataAndCheckStatus(): UseSaveXlsxImportDataAndCheckStatusReturnType {
  const [loading, setLoading] = useState(false);
  const [
    saveXlsxImportDataMutate,
    { data: xlsxImportDataFromMutation },
  ] = useUploadImportDataXlsxFileAsyncMutation();
  const [loadImportData, { data: xlsxImportData }] = useXlsxImportDataLazyQuery(
    {
      variables: {
        id:
          xlsxImportDataFromMutation?.uploadImportDataXlsxFileAsync?.importData
            ?.id,
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
    if (xlsxImportDataFromMutation?.uploadImportDataXlsxFileAsync?.importData) {
      startPollingImportData({
        id:
          xlsxImportDataFromMutation.uploadImportDataXlsxFileAsync.importData
            .id,
      });
    }
  }, [xlsxImportDataFromMutation]);
  useEffect(() => {
    if (!xlsxImportData) {
      return;
    }
    if (
      [
        ImportDataStatus.Error,
        ImportDataStatus.ValidationError,
        ImportDataStatus.Finished,
      ].includes(xlsxImportData?.importData?.status)
    ) {
      stopPollingImportData();
      setLoading(false);
    }
  }, [xlsxImportData]);
  const saveAndStartPolling = async (
    variables: UploadImportDataXlsxFileAsyncMutationVariables,
  ): Promise<void> => {
    try {
      setLoading(true);
      await saveXlsxImportDataMutate({ variables });
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };
  return {
    saveAndStartPolling,
    stopPollingImportData,
    loading,
    xlsxImportData: xlsxImportData?.importData,
  };
}
