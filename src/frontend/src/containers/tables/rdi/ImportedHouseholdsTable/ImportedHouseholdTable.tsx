import {
  AllHouseholdsQueryVariables,
  AllImportedHouseholdsQueryVariables,
  HouseholdMinimalFragment,
  HouseholdRdiMergeStatus,
  ImportedHouseholdMinimalFragment,
  useAllHouseholdsQuery,
} from '@generated/graphql';
import { ReactElement } from 'react';
import { UniversalTable } from '../../UniversalTable';
import { headCells as importedHeadCells } from './ImportedHouseholdTableHeadCells';
import { ImportedHouseholdTableRow } from './ImportedHouseholdTableRow';
import { headCells as mergedHeadCells } from './MergedHouseholdTableHeadCells';

export function ImportedHouseholdTable({
  rdi,
  businessArea,
  isMerged,
}): ReactElement {
  const initialVariables = {
    rdiId: rdi.id,
    businessArea,
    rdiMergeStatus: isMerged
      ? HouseholdRdiMergeStatus.Merged
      : HouseholdRdiMergeStatus.Pending,
  };

  if (isMerged) {
    return (
      <UniversalTable<HouseholdMinimalFragment, AllHouseholdsQueryVariables>
        headCells={mergedHeadCells}
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
    <UniversalTable<
      ImportedHouseholdMinimalFragment,
      AllImportedHouseholdsQueryVariables
    >
      headCells={importedHeadCells}
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
