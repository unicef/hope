import {
  AllHouseholdsQueryVariables,
  HouseholdMinimalFragment,
  HouseholdRdiMergeStatus,
  useAllHouseholdsQuery,
} from '@generated/graphql';
import { ReactElement } from 'react';
import { UniversalTable } from '../../UniversalTable';
import { headCells as importedHeadCells } from './ImportedHouseholdTableHeadCells';
import { ImportedHouseholdTableRow } from './ImportedHouseholdTableRow';
import { headCells as mergedHeadCells } from './MergedHouseholdTableHeadCells';
import { useProgramContext } from 'src/programContext';
import { adjustHeadCells } from '@utils/utils';
import withErrorBoundary from '@components/core/withErrorBoundary';

function ImportedHouseholdTable({ rdi, businessArea, isMerged }): ReactElement {
  const initialVariables = {
    rdiId: rdi.id,
    businessArea
  };

  const { selectedProgram } = useProgramContext();
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
      <UniversalTable<HouseholdMinimalFragment, AllHouseholdsQueryVariables>
        headCells={adjustedMergedHeadCells}
        query={useAllHouseholdsQuery}
        queriedObjectName="allHouseholds"
        rowsPerPageOptions={[10, 15, 20]}
        initialVariables={initialVariables}
        isOnPaper={false}
        renderRow={(row) => (
          <ImportedHouseholdTableRow
            rdi={rdi}
            isMerged={isMerged}
            key={row.id}
            household={row}
          />
        )}
      />
    );
  }
  return (
    <UniversalTable<HouseholdMinimalFragment, AllHouseholdsQueryVariables>
      headCells={adjustedImportedHeadCells}
      query={useAllHouseholdsQuery}
      queriedObjectName="allHouseholds"
      rowsPerPageOptions={[10, 15, 20]}
      initialVariables={initialVariables}
      isOnPaper={false}
      renderRow={(row) => (
        <ImportedHouseholdTableRow
          rdi={rdi}
          isMerged={isMerged}
          key={row.id}
          household={row}
        />
      )}
    />
  );
}

export default withErrorBoundary(
  ImportedHouseholdTable,
  'ImportedHouseholdTable',
);
