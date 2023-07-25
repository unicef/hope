import React, { ReactElement } from 'react';
import {
  AllImportedHouseholdsQueryVariables,
  AllMergedHouseholdsQueryVariables,
  ImportedHouseholdMinimalFragment,
  MergedHouseholdMinimalFragment,
  useAllImportedHouseholdsQuery,
  useAllMergedHouseholdsQuery
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { ImportedHouseholdTableRow } from './ImportedHouseholdTableRow';
import { headCells as importedHeadCells } from './ImportedHouseholdTableHeadCells';
import { headCells as mergedHeadCells } from './MergedHouseholdTableHeadCells';

export function ImportedHouseholdTable({ rdiId, businessArea, isMerged }): ReactElement {
  const initialVariables = {
    rdiId,
    businessArea,
  };

  if (isMerged) {
    return (
        <UniversalTable<
          MergedHouseholdMinimalFragment,
          AllMergedHouseholdsQueryVariables
        >
          headCells={mergedHeadCells}
          query={useAllMergedHouseholdsQuery}
          queriedObjectName='allMergedHouseholds'
          rowsPerPageOptions={[10, 15, 20]}
          initialVariables={initialVariables}
          isOnPaper={false}
          renderRow={(row) => (
            <ImportedHouseholdTableRow isMerged={isMerged} key={row.id} household={row} />
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
      query={useAllImportedHouseholdsQuery}
      queriedObjectName='allImportedHouseholds'
      rowsPerPageOptions={[10, 15, 20]}
      initialVariables={initialVariables}
      isOnPaper={false}
      renderRow={(row) => (
        <ImportedHouseholdTableRow isMerged={isMerged} key={row.id} household={row} />
      )}
    />
  );
}
