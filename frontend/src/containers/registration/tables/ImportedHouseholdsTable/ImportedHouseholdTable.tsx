import React, { ReactElement } from 'react';
import {
  AllImportedHouseholdsQueryVariables,
  ImportedHouseholdMinimalFragment,
  useAllImportedHouseholdsQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../../tables/UniversalTable';
import { ImportedHouseholdTableRow } from './ImportedHouseholdTableRow';
import { headCells } from './ImportedHouseholdTableHeadCells';

export function ImportedHouseholdTable({ rdiId }): ReactElement {
  const initialVariables = {
    rdiId,
  };
  return (
    <UniversalTable<
      ImportedHouseholdMinimalFragment,
      AllImportedHouseholdsQueryVariables
    >
      headCells={headCells}
      query={useAllImportedHouseholdsQuery}
      queriedObjectName='allImportedHouseholds'
      rowsPerPageOptions={[10, 15, 20]}
      initialVariables={initialVariables}
      isOnPaper={false}
      renderRow={(row) => <ImportedHouseholdTableRow household={row} />}
    />
  );
}
