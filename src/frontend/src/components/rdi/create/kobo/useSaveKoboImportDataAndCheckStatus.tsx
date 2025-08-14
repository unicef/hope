/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useState } from 'react';
import { RestService } from '@restgenerated/services/RestService';
import { useLazyInterval } from '@hooks/useInterval';
import { KoboImportData } from '@restgenerated/models/KoboImportData';
import { Status753Enum } from '@restgenerated/models/Status753Enum';
import { useMutation, useQuery } from '@tanstack/react-query';

interface SaveKoboVariables {
  businessAreaSlug: string;
  programSlug: string;
  koboAssetId: string;
  onlyActiveSubmissions: boolean;
  pullPictures: boolean;
}

export interface UseSaveKoboImportDataAndCheckStatusReturnType {
  saveAndStartPolling: (
    variables: SaveKoboVariables,
  ) => Promise<void>;
  stopPollingImportData: () => void;
  loading: boolean;
  koboImportData: KoboImportData | null;
}

export function useSaveKoboImportDataAndCheckStatus(): UseSaveKoboImportDataAndCheckStatusReturnType {
  const [importDataId, setImportDataId] = useState<string | null>(null);
  const [businessAreaSlug, setBusinessAreaSlug] = useState<string | null>(null);

  // Mutation for saving Kobo import data
  const saveMutation = useMutation({
    mutationFn: async (variables: SaveKoboVariables) => {
      return RestService.restBusinessAreasProgramsKoboImportDataUploadSaveKoboImportDataCreate({
        businessAreaSlug: variables.businessAreaSlug,
        programSlug: variables.programSlug,
        requestBody: {
          uid: variables.koboAssetId,
          onlyActiveSubmissions: variables.onlyActiveSubmissions,
          pullPictures: variables.pullPictures,
        },
      });
    },
    onSuccess: (data) => {
      setImportDataId(data.id);
      setBusinessAreaSlug(data.businessAreaSlug);
    },
  });

  // Query for polling kobo import data status
  const { data: koboImportData, refetch } = useQuery({
    queryKey: ['koboImportData', importDataId, businessAreaSlug],
    queryFn: async () => {
      if (!importDataId || !businessAreaSlug) return null;
      return RestService.restBusinessAreasKoboImportDataRetrieve({
        businessAreaSlug: businessAreaSlug,
        id: importDataId,
      });
    },
    enabled: !!importDataId && !!businessAreaSlug,
    refetchInterval: (data) => {
      // Stop polling if status is final
      if (data && [
        Status753Enum.ERROR,
        Status753Enum.VALIDATION_ERROR,
        Status753Enum.FINISHED,
      ].includes(data.status)) {
        return false;
      }
      return 3000; // Poll every 3 seconds
    },
  });

  const [startPollingImportData, stopPollingImportData] = useLazyInterval(
    () => refetch(),
    3000,
  );

  useEffect(() => {
    if (importDataId && businessAreaSlug) {
      startPollingImportData();
    }
  }, [importDataId, businessAreaSlug]);

  useEffect(() => {
    if (koboImportData && [
      Status753Enum.ERROR,
      Status753Enum.VALIDATION_ERROR,
      Status753Enum.FINISHED,
    ].includes(koboImportData.status)) {
      stopPollingImportData();
    }
  }, [koboImportData]);

  const saveAndStartPolling = async (variables: SaveKoboVariables): Promise<void> => {
    return saveMutation.mutateAsync(variables);
  };

  return {
    saveAndStartPolling,
    stopPollingImportData,
    loading: saveMutation.isPending,
    koboImportData: koboImportData || null,
  };
}
