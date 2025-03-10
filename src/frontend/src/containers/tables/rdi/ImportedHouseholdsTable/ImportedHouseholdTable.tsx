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

function ImportedHouseholdTable({ rdi, businessArea, isMerged }): ReactElement {
  const { selectedProgram } = useProgramContext();

  const initialQueryVariables = useMemo(
    () => ({
      rdiId: rdi.id,
      businessAreaSlug: businessArea,
      programProgrammeCode: selectedProgram?.programmeCode,
      rdiMergeStatus: isMerged
        ? HouseholdRdiMergeStatus.Merged
        : HouseholdRdiMergeStatus.Pending,
    }),
    [rdi, businessArea, isMerged, selectedProgram?.programmeCode],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const { data, isLoading, error } = useQuery({
    queryKey: [
      'businessAreasProgramsHouseholdsList',
      queryVariables,
      selectedProgram?.programmeCode,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsList(queryVariables),
    enabled: !!businessArea && !!selectedProgram?.programmeCode,
  });

  const beneficiaryGroup = selectedProgram?.beneficiary_group;

  const mergedReplacements = {
    id: (_beneficiaryGroup) => `${_beneficiaryGroup?.member_label} ID`,
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
            isMerged={isMerged}
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
          isMerged={isMerged}
          key={(row as any).id}
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
