/* eslint-disable react-hooks/exhaustive-deps */
import { useState } from 'react';
import { RestService } from '@restgenerated/services/RestService';
import { ImportData } from '@restgenerated/models/ImportData';
import { Status753Enum } from '@restgenerated/models/Status753Enum';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface SaveXlsxVariables {
  businessAreaSlug: string;
  programSlug: string;
  file: File;
}

export interface UseSaveXlsxImportDataAndCheckStatusReturnType {
  saveAndStartPolling: (variables: SaveXlsxVariables) => Promise<void>;
  loading: boolean;
  xlsxImportData: ImportData | null;
}

export function useSaveXlsxImportDataAndCheckStatus(): UseSaveXlsxImportDataAndCheckStatusReturnType {
  const [importDataId, setImportDataId] = useState<string | null>(null);
  const { businessAreaSlug } = useBaseUrl();

  // Mutation for uploading XLSX file
  const uploadMutation = useMutation({
    mutationFn: async (variables: SaveXlsxVariables) => {
      const formData = {
        file: variables.file,
      } as any;
      return RestService.restBusinessAreasProgramsImportDataUploadUploadXlsxFileCreate(
        {
          businessAreaSlug: variables.businessAreaSlug,
          programSlug: variables.programSlug,
          formData,
        },
      );
    },
    onSuccess: (data) => {
      setImportDataId(data.id);
    },
  });

  // Query for polling import data status
  const { data: xlsxImportData } = useQuery({
    queryKey: ['importData', importDataId, businessAreaSlug],
    queryFn: async () => {
      if (!importDataId || !businessAreaSlug) return null;
      return RestService.restBusinessAreasImportDataRetrieve({
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

  const saveAndStartPolling = async (
    variables: SaveXlsxVariables,
  ): Promise<void> => {
    await uploadMutation.mutateAsync(variables);
  };

  return {
    saveAndStartPolling,
    loading:
      uploadMutation.isPending ||
      [Status753Enum.PENDING, Status753Enum.RUNNING].includes(
        xlsxImportData?.status,
      ),
    xlsxImportData: xlsxImportData || null,
  };
}
