import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { HouseholdRdiMergeStatus } from '@generated/graphql';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useMemo, useState } from 'react';
import { useProgramContext } from 'src/programContext';
import { headCells as importedHeadCells } from './ImportedHouseholdTableHeadCells';
import { ImportedHouseholdTableRow } from './ImportedHouseholdTableRow';
import { headCells as mergedHeadCells } from './MergedHouseholdTableHeadCells';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { PaginatedHouseholdListList } from '@restgenerated/models/PaginatedHouseholdListList';

function ImportedHouseholdTable({ rdi, businessArea, isMerged }): ReactElement {
  const { selectedProgram } = useProgramContext();
  const { programId } = useBaseUrl();

  const initialQueryVariables = useMemo(
    () => ({
      rdiId: rdi.id,
      businessAreaSlug: businessArea,
      programSlug: programId,
      rdiMergeStatus: isMerged
        ? HouseholdRdiMergeStatus.Merged
        : HouseholdRdiMergeStatus.Pending,
    }),
    [rdi, businessArea, isMerged, programId],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const { data, isLoading, error } = useQuery<PaginatedHouseholdListList>({
    queryKey: [
      'businessAreasProgramsHouseholdsList',
      queryVariables,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsList(queryVariables),
    enabled: !!businessArea && !!programId,
  });

  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const mergedReplacements = {
    id: (_beneficiaryGroup) => `${_beneficiaryGroup?.memberLabel} ID`,
    head_of_household__full_name: (_beneficiaryGroup) =>
      `Head of ${_beneficiaryGroup?.groupLabel}`,
    size: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} Size`,
  };

  const adjustedMergedHeadCells = adjustHeadCells(
    mergedHeadCells,
    beneficiaryGroup,
    mergedReplacements,
  );

  const importedReplacements = {
    id: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} ID`,
    head_of_household__full_name: (_beneficiaryGroup) =>
      `Head of ${_beneficiaryGroup?.groupLabel}`,
    size: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} Size`,
  };

  const adjustedImportedHeadCells = adjustHeadCells(
    importedHeadCells,
    beneficiaryGroup,
    importedReplacements,
  );
  if (isMerged) {
    return (
      <UniversalRestTable
        renderRow={(row) => (
          <ImportedHouseholdTableRow
            rdi={rdi}
            key={(row as any).id}
            household={row}
          />
        )}
        headCells={adjustedMergedHeadCells}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        data={data}
        isLoading={isLoading}
        error={error}
      />
    );
  }
  return (
    <UniversalRestTable
      renderRow={(row) => (
        <ImportedHouseholdTableRow
          rdi={rdi}
          key={(row as HouseholdDetail).id}
          household={row}
        />
      )}
      headCells={adjustedImportedHeadCells}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      data={data}
      isLoading={isLoading}
      error={error}
    />
  );
}

export default withErrorBoundary(
  ImportedHouseholdTable,
  'ImportedHouseholdTable',
);
