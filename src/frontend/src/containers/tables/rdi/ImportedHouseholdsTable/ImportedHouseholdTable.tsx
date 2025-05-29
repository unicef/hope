import withErrorBoundary from '@components/core/withErrorBoundary';
import { HouseholdRdiMergeStatus } from '@generated/graphql';
import { RestService } from '@restgenerated/services/RestService';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useProgramContext } from 'src/programContext';
import { headCells as importedHeadCells } from './ImportedHouseholdTableHeadCells';
import { ImportedHouseholdTableRow } from './ImportedHouseholdTableRow';
import { headCells as mergedHeadCells } from './MergedHouseholdTableHeadCells';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { UniversalRestQueryTable } from '@components/rest/UniversalRestQueryTable/UniversalRestQueryTable';

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
    [rdi.id, businessArea, programId, isMerged],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

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
      <UniversalRestQueryTable
        isOnPaper={false}
        renderRow={(row) => (
          <ImportedHouseholdTableRow rdi={rdi} key={row.id} household={row} />
        )}
        query={RestService.restBusinessAreasProgramsHouseholdsList}
        headCells={adjustedMergedHeadCells}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
      />
    );
  }
  return (
    <UniversalRestQueryTable
      isOnPaper={false}
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
      query={RestService.restBusinessAreasProgramsHouseholdsList}
    />
  );
}

export default withErrorBoundary(
  ImportedHouseholdTable,
  'ImportedHouseholdTable',
);
