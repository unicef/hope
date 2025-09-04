/* eslint-disable react-hooks/exhaustive-deps */
import { useState } from 'react';
import { RestService } from '@restgenerated/services/RestService';
import { KoboImportData } from '@restgenerated/models/KoboImportData';
import { Status753Enum } from '@restgenerated/models/Status753Enum';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface SaveKoboVariables {
  businessAreaSlug: string;
  programSlug: string;
  koboAssetId: string;
  onlyActiveSubmissions: boolean;
  pullPictures: boolean;
}

export interface UseSaveKoboImportDataAndCheckStatusReturnType {
  saveAndStartPolling: (variables: SaveKoboVariables) => void;
  loading: boolean;
  koboImportData: KoboImportData | null;
}

export function useSaveKoboImportDataAndCheckStatus(): UseSaveKoboImportDataAndCheckStatusReturnType {
  const [importDataId, setImportDataId] = useState<string | null>(null);
  const { businessAreaSlug } = useBaseUrl();

  // Mutation for saving Kobo import data
  const saveMutation = useMutation({
    mutationFn: async (variables: SaveKoboVariables) => {
      return RestService.restBusinessAreasProgramsKoboImportDataUploadSaveKoboImportDataCreate(
        {
          businessAreaSlug: variables.businessAreaSlug,
          programSlug: variables.programSlug,
          requestBody: {
            uid: variables.koboAssetId,
            onlyActiveSubmissions: variables.onlyActiveSubmissions,
            pullPictures: variables.pullPictures,
          },
        },
      );
    },
    onSuccess: (data) => {
      setImportDataId(data.id);
    },
  });

  // Query for polling kobo import data status
  const { data: koboImportData } = useQuery({
    queryKey: ['koboImportData', importDataId, businessAreaSlug],
    queryFn: async () => {
      if (!importDataId || !businessAreaSlug) return null;
      return RestService.restBusinessAreasKoboImportDataRetrieve({
        businessAreaSlug: businessAreaSlug,
        id: importDataId,
      });
    },
    enabled: !!importDataId,
    refetchInterval: (data) => {
      // Stop polling if status is final
      if (
        data &&
        [
          Status753Enum.ERROR,
          Status753Enum.VALIDATION_ERROR,
          Status753Enum.FINISHED,
        ].includes(data?.state?.data?.status)
      ) {
        return false;
      }
      return 3000; // Poll every 3 seconds
    },
  });

  const saveAndStartPolling = (variables: SaveKoboVariables): void => {
    saveMutation.mutateAsync(variables);
  };

  return {
    saveAndStartPolling,
    loading:
      saveMutation.isPending ||
      [Status753Enum.PENDING, Status753Enum.RUNNING].includes(
        koboImportData?.status,
      ),
    koboImportData: koboImportData || null,
  };
}
