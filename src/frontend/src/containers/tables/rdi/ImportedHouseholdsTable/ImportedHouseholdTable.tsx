import withErrorBoundary from '@components/core/withErrorBoundary';
import { RestService } from '@restgenerated/services/RestService';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useProgramContext } from 'src/programContext';
import { headCells as importedHeadCells } from './ImportedHouseholdTableHeadCells';
import { ImportedHouseholdTableRow } from './ImportedHouseholdTableRow';
import { headCells as mergedHeadCells } from './MergedHouseholdTableHeadCells';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { UniversalRestQueryTable } from '@components/rest/UniversalRestQueryTable/UniversalRestQueryTable';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { RegistrationDataImportStatusEnum } from '@restgenerated/models/RegistrationDataImportStatusEnum';

function ImportedHouseholdTable({ rdi, businessArea, isMerged }): ReactElement {
  const { selectedProgram } = useProgramContext();
  const { programId } = useBaseUrl();
  const [page, setPage] = useState(0);
  const notAllowedRdiShowPreviewStatuses = [
    RegistrationDataImportStatusEnum.LOADING,
    RegistrationDataImportStatusEnum.IMPORTING,
    RegistrationDataImportStatusEnum.IMPORT_SCHEDULED,
    RegistrationDataImportStatusEnum.IMPORT_ERROR,
  ];

  const initialQueryVariables = useMemo(
    () => ({
      rdiId: rdi.id,
      businessAreaSlug: businessArea,
      programSlug: programId,
      rdiMergeStatus: isMerged ? 'MERGED' : 'PENDING',
    }),
    [rdi.id, businessArea, programId, isMerged],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const { data: countData } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsHouseholdsCount',
      programId,
      businessArea,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsCountRetrieve(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
        ),
      ),
    enabled: page === 0 && !notAllowedRdiShowPreviewStatuses.includes(rdi.status),
  });

  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const mergedReplacements = {
    unicefId: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} ID`,
    head_of_household__full_name: (_beneficiaryGroup) =>
      `Head of ${_beneficiaryGroup?.groupLabel}`,
    size: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} Size`,
  };

  const adjustedMergedHeadCells = adjustHeadCells(
    mergedHeadCells,
    beneficiaryGroup,
    mergedReplacements,
  );

  const itemsCount = usePersistedCount(page, countData);

  const importedReplacements = {
    unicefId: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} ID`,
    head_of_household__full_name: (_beneficiaryGroup) =>
      `Head of ${_beneficiaryGroup?.groupLabel}`,
    size: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} Size`,
  };

  const adjustedImportedHeadCells = adjustHeadCells(
    importedHeadCells,
    beneficiaryGroup,
    importedReplacements,
  );

  return (
    <UniversalRestQueryTable
      isOnPaper={false}
      renderRow={(row) => (
        <ImportedHouseholdTableRow rdi={rdi} key={row.id} household={row} />
      )}
      query={RestService.restBusinessAreasProgramsHouseholdsList}
      headCells={isMerged ? adjustedMergedHeadCells : adjustedImportedHeadCells}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      page={page}
      setPage={setPage}
      itemsCount={itemsCount}
      customEnabled={!notAllowedRdiShowPreviewStatuses.includes(rdi.status)}
    />
  );
}

export default withErrorBoundary(
  ImportedHouseholdTable,
  'ImportedHouseholdTable',
);
