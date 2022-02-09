/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useState } from 'react';
import {
  ImportDataStatus,
  KoboImportDataQueryResult,
  SaveKoboImportDataAsyncMutationVariables,
  UploadImportDataXlsxFileMutationVariables,
  useKoboImportDataLazyQuery,
  useSaveKoboImportDataAsyncMutation,
  useUploadImportDataXlsxFileMutation,
  useXlsxImportDataLazyQuery,
  useXlsxImportDataQuery,
  XlsxImportDataQuery,
  XlsxImportDataQueryResult,
} from '../../../../__generated__/graphql';
import { useLazyInterval } from '../../../../hooks/useInterval';

export interface UseSaveXlsxImportDataAndCheckStatusReturnType {
  saveAndStartPolling: (
    variables: UploadImportDataXlsxFileMutationVariables,
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
  ] = useUploadImportDataXlsxFileMutation();
  const [
    loadImportData,
    { data: xlsxImportData, error: error1 },
  ] = useXlsxImportDataLazyQuery({
    variables: {
      id: xlsxImportDataFromMutation?.uploadImportDataXlsxFile?.importData?.id,
    },
    fetchPolicy: 'network-only',
  });
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
    if (xlsxImportDataFromMutation?.uploadImportDataXlsxFile?.importData) {
      startPollingImportData({
        id: xlsxImportDataFromMutation.uploadImportDataXlsxFile.importData.id,
      });
    }
  }, [xlsxImportDataFromMutation]);
  console.log('xlsxImportData', xlsxImportData, error1);
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
    variables: UploadImportDataXlsxFileMutationVariables,
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
