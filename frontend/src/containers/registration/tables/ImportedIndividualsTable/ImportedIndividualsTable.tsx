import React, { ReactElement } from 'react';
import styled from 'styled-components';
import {
  AllImportedHouseholdsQueryVariables,
  AllImportedIndividualsQueryVariables,
  ImportedHouseholdMinimalFragment,
  ImportedIndividualMinimalFragment,
  useAllImportedHouseholdsQuery,
  useAllImportedIndividualsQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../../tables/UniversalTable';
import { ImportedIndividualsTableRow } from './ImportedIndividualsTableRow';
import { headCells } from './ImportedIndividualsTableHeadCells';

export function ImportedIndividualsTable({ rdiId }): ReactElement {
  const initialVariables = {
    rdiId,
  };
  return (
    <UniversalTable<
      ImportedIndividualMinimalFragment,
      AllImportedIndividualsQueryVariables
    >
      headCells={headCells}
      query={useAllImportedIndividualsQuery}
      queriedObjectName='allImportedIndividuals'
      rowsPerPageOptions={[10,15,20]}
      initialVariables={initialVariables}
      isOnPaper={false}
      renderRow={(row) => <ImportedIndividualsTableRow individual={row} />}
    />
  );
}
